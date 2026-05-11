from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from questions import mix_questions, Question, export_questions_to_docx
from database import load_questions_from_mongodb, save_questions_to_mongodb, append_questions_to_mongodb
import json
import pandas as pd
import io
import zipfile
from docx import Document
import re

app = Flask(__name__)
CORS(app)

@app.route('/api/admin/upload-json', methods=['POST'])
def upload_json():
    if 'file' not in request.files:
        return jsonify({'status': 'error', 'message': 'Không tìm thấy file tải lên.'}), 400
    
    file = request.files['file']
    mode = request.form.get('mode', 'append') # 'append' or 'overwrite'
    
    if file.filename == '':
        return jsonify({'status': 'error', 'message': 'Chưa chọn file.'}), 400
        
    if file and file.filename.endswith('.json'):
        try:
            data = json.load(file)
            questions = [Question.from_dict(item) for item in data]
            
            if mode == 'overwrite':
                save_questions_to_mongodb(questions)
                msg = f'Đã ghi đè thành công {len(questions)} câu hỏi vào Database.'
            else:
                inserted, skipped = append_questions_to_mongodb(questions)
                msg = f'Đã thêm mới {inserted} câu hỏi. Bỏ qua {skipped} câu trùng lặp.'
                
            return jsonify({
                'status': 'success', 
                'message': msg
            })
        except Exception as e:
            return jsonify({'status': 'error', 'message': f'Lỗi khi xử lý file JSON: {str(e)}'}), 500
            
    return jsonify({'status': 'error', 'message': 'Định dạng không hợp lệ. Vui lòng tải lên file .json.'}), 400

@app.route('/api/admin/upload-excel', methods=['POST'])
def upload_excel():
    if 'file' not in request.files:
        return jsonify({'status': 'error', 'message': 'Không tìm thấy file tải lên.'}), 400
    
    file = request.files['file']
    mode = request.form.get('mode', 'append')
    
    if file.filename == '':
        return jsonify({'status': 'error', 'message': 'Chưa chọn file.'}), 400
        
    if file and (file.filename.endswith('.xlsx') or file.filename.endswith('.xls')):
        try:
            df = pd.read_excel(file)
            df.columns = df.columns.str.strip()
            questions = []
            
            # Giả sử cấu trúc cột Excel là: ID, Question, Option A, Option B, Option C, Option D, Answer, Difficulty, Topic
            for index, row in df.iterrows():
                try:
                    q = Question(
                        id=str(row['ID']) if pd.notna(row['ID']) else str(index+1),
                        question=str(row['Question']),
                        options={
                            "A": str(row['A']),
                            "B": str(row['B']),
                            "C": str(row['C']),
                            "D": str(row['D'])
                        },
                        answer=str(row['Answer']).upper().strip(),
                        difficulty=str(row['Difficulty']).strip() if pd.notna(row['Difficulty']) else "Medium",
                        topic=str(row['Topic']).strip() if pd.notna(row['Topic']) else "General"
                    )
                    questions.append(q)
                except Exception as ex:
                    print(f"Bỏ qua dòng {index+2} do lỗi dữ liệu: {ex}")
                    continue
            
            if len(questions) == 0:
                 return jsonify({'status': 'error', 'message': 'Không tìm thấy câu hỏi hợp lệ trong file Excel.'}), 400
                 
            if mode == 'overwrite':
                save_questions_to_mongodb(questions)
                msg = f'Đã ghi đè thành công {len(questions)} câu hỏi từ Excel vào Database.'
            else:
                inserted, skipped = append_questions_to_mongodb(questions)
                msg = f'Đã thêm mới {inserted} câu hỏi từ Excel. Bỏ qua {skipped} câu trùng lặp.'
                
            return jsonify({
                'status': 'success', 
                'message': msg
            })
        except Exception as e:
            return jsonify({'status': 'error', 'message': f'Lỗi khi xử lý file Excel: {str(e)}'}), 500
            
    return jsonify({'status': 'error', 'message': 'Định dạng không hợp lệ. Vui lòng tải lên file .xlsx hoặc .xls.'}), 400

@app.route('/api/admin/upload-word', methods=['POST'])
def upload_word():
    if 'file' not in request.files:
        return jsonify({'status': 'error', 'message': 'Không tìm thấy file tải lên.'}), 400
    
    file = request.files['file']
    mode = request.form.get('mode', 'append')
    
    if file.filename == '':
        return jsonify({'status': 'error', 'message': 'Chưa chọn file.'}), 400
        
    if file and file.filename.endswith('.docx'):
        try:
            doc = Document(file)
            questions = []
            
            current_question = None
            for p in doc.paragraphs:
                text = p.text.strip()
                if not text:
                    continue
                
                q_match = re.match(r'^(?i)(?:câu|question|bài)\s*\d+[\.\:\-\/]?\s*(.*)', text)
                opt_match = re.match(r'^(?i)([a-d])[\.\:\)\-\/]\s*(.*)', text)
                ans_match = re.match(r'^(?i)(?:đáp án|answer|đáp án đúng)[\:\-\s]*([a-d])', text)
                diff_match = re.match(r'^(?i)(?:mức độ|độ khó|difficulty)[\:\-\s]*(.*)', text)
                topic_match = re.match(r'^(?i)(?:chủ đề|topic)[\:\-\s]*(.*)', text)

                if q_match:
                    # Save previous question if exists
                    if current_question and getattr(current_question, 'question', None) and len(getattr(current_question, 'options', {})) >= 2 and getattr(current_question, 'answer', None):
                        questions.append(current_question)
                    
                    q_text = q_match.group(1).strip()
                    if not q_text:
                        q_text = text # Fallback in case question text is empty on first line
                        
                    current_question = Question(
                        id=str(len(questions) + 1),
                        question=q_text,
                        options={},
                        answer="",
                        difficulty="Medium",
                        topic="General"
                    )
                elif current_question:
                    if opt_match:
                        opt_key = opt_match.group(1).upper()
                        opt_text = opt_match.group(2).strip()
                        current_question.options[opt_key] = opt_text
                    elif ans_match:
                        current_question.answer = ans_match.group(1).upper()
                    elif diff_match:
                        current_question.difficulty = diff_match.group(1).strip()
                    elif topic_match:
                        current_question.topic = topic_match.group(1).strip()
                    else:
                        # Append multiline text to the question if options haven't started
                        if len(current_question.options) == 0:
                            current_question.question += "\n" + text
                            
            if current_question and getattr(current_question, 'question', None) and len(getattr(current_question, 'options', {})) >= 2 and getattr(current_question, 'answer', None):
                questions.append(current_question)
            
            for idx, q in enumerate(questions):
                q.id = str(idx + 1)
                
            if len(questions) == 0:
                 return jsonify({'status': 'error', 'message': 'Không tìm thấy câu hỏi hợp lệ trong file Word.'}), 400
                 
            if mode == 'overwrite':
                save_questions_to_mongodb(questions)
                msg = f'Đã ghi đè thành công {len(questions)} câu hỏi từ Word vào Database.'
            else:
                inserted, skipped = append_questions_to_mongodb(questions)
                msg = f'Đã thêm mới {inserted} câu hỏi từ Word. Bỏ qua {skipped} câu trùng lặp.'
                
            return jsonify({
                'status': 'success', 
                'message': msg
            })
        except Exception as e:
            return jsonify({'status': 'error', 'message': f'Lỗi khi xử lý file Word: {str(e)}'}), 500
            
    return jsonify({'status': 'error', 'message': 'Định dạng không hợp lệ. Vui lòng tải lên file .docx.'}), 400

@app.route('/api/generate-exams', methods=['POST'])
def generate_exams():
    try:
        req_data = request.get_json(silent=True) or {}
        num_exams = int(req_data.get('num_exams', 1))
        prefix = req_data.get('prefix', 'DeThi')

        if num_exams < 1 or num_exams > 50:
            return jsonify({'status': 'error', 'message': 'Số lượng đề thi phải từ 1 đến 50.'}), 400

        all_questions = load_questions_from_mongodb()
        if not all_questions:
            return jsonify({'status': 'error', 'message': 'Chưa có câu hỏi nào trong Database.'}), 400

        mem_zip = io.BytesIO()
        
        with zipfile.ZipFile(mem_zip, mode='w', compression=zipfile.ZIP_DEFLATED) as zf:
            for i in range(num_exams):
                exam_code = f"{prefix}_{i+1:03d}"
                # Xáo trộn câu hỏi
                mixed = mix_questions(all_questions)
                
                # Tạo file docx trên RAM
                mem_doc = io.BytesIO()
                export_questions_to_docx(mixed, exam_code, filename=mem_doc)
                
                # Lưu vào Zip
                zf.writestr(f"{exam_code}.docx", mem_doc.getvalue())
                
        mem_zip.seek(0)
        
        return send_file(
            mem_zip,
            mimetype='application/zip',
            as_attachment=True,
            download_name=f'DeThi_{prefix}.zip'
        )

    except Exception as e:
        print(e)
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
