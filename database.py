import os
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from questions import Question

# Tải biến môi trường từ file .env
load_dotenv()

def get_db():
    uri = os.getenv("MONGODB_URI")
    if not uri:
        raise ValueError("Chưa cấu hình MONGODB_URI trong file .env")
    
    # Tạo kết nối đến MongoDB kèm theo chứng chỉ bảo mật SSL/TLS
    import certifi
    client = MongoClient(uri, server_api=ServerApi('1'), tlsCAFile=certifi.where())
    
    # Kiểm tra kết nối
    try:
        client.admin.command('ping')
        print("Đã kết nối thành công tới MongoDB!")
    except Exception as e:
        print("Lỗi kết nối MongoDB:", e)
        
    return client[os.getenv("DB_NAME")]

def load_questions_from_mongodb():
    db = get_db()
    collection = db[os.getenv("COLLECTION_NAME")]
    data = list(collection.find({}))
    if not data:
        print("Không có câu hỏi nào trong MongoDB.")
        return []
    questions = [Question.from_dict(item) for item in data]
    return questions

def save_questions_to_mongodb(questions):
    db = get_db()
    collection = db[os.getenv("COLLECTION_NAME")]
    
    # Xoá dữ liệu cũ (tuỳ chọn, để tránh trùng lặp khi chạy nhiều lần)
    collection.delete_many({}) 
    
    data = [question.to_dict() for question in questions]
    if data:
        collection.insert_many(data)
    print("Đã GHI ĐÈ các câu hỏi vào MongoDB.")

def append_questions_to_mongodb(questions):
    db = get_db()
    collection = db[os.getenv("COLLECTION_NAME")]
    
    # Lấy danh sách nội dung câu hỏi hiện có để kiểm tra trùng lặp
    existing_docs = collection.find({}, {"question": 1})
    existing_texts = {doc.get("question", "").strip().lower() for doc in existing_docs}
    
    new_data = []
    for q in questions:
        q_text = q.question.strip().lower()
        if q_text not in existing_texts:
            new_data.append(q.to_dict())
            existing_texts.add(q_text) # Tránh trùng lặp ngay trong chính file đang tải lên
            
    if new_data:
        collection.insert_many(new_data)
        
    inserted = len(new_data)
    skipped = len(questions) - inserted
    print(f"Đã THÊM MỚI {inserted} câu hỏi. Bỏ qua {skipped} câu trùng lặp.")
    return inserted, skipped
