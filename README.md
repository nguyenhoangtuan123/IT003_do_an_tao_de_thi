# Ứng dụng Quản lý & Sinh Đề Thi Trắc Nghiệm Tự Động (IT003)

Đây là đồ án môn học **IT003**, một ứng dụng Web (Web Application) quản lý ngân hàng câu hỏi trắc nghiệm và hỗ trợ tự động sinh đề thi, trộn đề và xuất đề thi hàng loạt.

## 🌟 Tính năng nổi bật
- **Đa dạng định dạng đầu vào**: Hỗ trợ tải lên ngân hàng câu hỏi từ nhiều loại file:
  - `.json`
  - `.xlsx` (Excel)
  - `.docx` (Word - hỗ trợ bóc tách dữ liệu thông minh bằng Regex)
- **Quản lý dữ liệu tập trung với MongoDB**: 
  - Lưu trữ toàn bộ câu hỏi.
  - Hỗ trợ chế độ Ghi đè (Overwrite) toàn bộ hoặc Thêm mới (Append).
  - Tự động nhận diện và loại bỏ các câu hỏi trùng lặp nội dung.
- **Thuật toán trộn đề tự động**: 
  - Sinh ra nhiều mã đề khác nhau từ ngân hàng câu hỏi.
  - Áp dụng thuật toán Fisher-Yates để xáo trộn vị trí câu hỏi.
  - Xáo trộn ngẫu nhiên thứ tự các đáp án (A, B, C, D) trong từng câu hỏi.
- **Trích xuất nhanh chóng**: 
  - Các đề thi được xuất ra định dạng Word (`.docx`).
  - Đóng gói toàn bộ các mã đề vào chung một file nén `.zip` và tự động tải xuống.
- **Giao diện hiện đại**: Frontend được xây dựng sử dụng Tailwind CSS, hỗ trợ upload file bất đồng bộ (AJAX) không cần tải lại trang.

## 🛠 Công nghệ sử dụng
- **Backend**: Python, Flask (RESTful API)
- **Database**: MongoDB
- **Thao tác file**: `python-docx` (xuất/nhập file Word), `pandas` (đọc file Excel), `zipfile`, `io`.
- **Frontend**: HTML5, Vanilla JavaScript, Tailwind CSS (qua CDN).

## 🚀 Hướng dẫn cài đặt và chạy ứng dụng

### 1. Yêu cầu hệ thống
- **Python** 3.8 trở lên.
- **MongoDB** đã được cài đặt và đang chạy (cục bộ hoặc dùng MongoDB Atlas).

### 2. Cài đặt môi trường ảo và thư viện
Mở Terminal/Command Prompt tại thư mục dự án và chạy các lệnh sau:

```bash
# Tạo môi trường ảo (tùy chọn nhưng khuyến khích)
python -m venv venv

# Kích hoạt môi trường ảo
# Trên Windows:
venv\Scripts\activate
# Trên macOS/Linux:
source venv/bin/activate

# Cài đặt các thư viện cần thiết
pip install flask pymongo python-docx pandas openpyxl python-dotenv
```

### 3. Cấu hình Cơ sở dữ liệu
Ứng dụng sử dụng file `.env` để quản lý biến môi trường. Đảm bảo bạn đã có file `.env` trong thư mục gốc với nội dung cấu hình MongoDB.
*Trong project đã có sẵn file `.env`, bạn có thể điều chỉnh đường dẫn (URI) đến database tại đây nếu cần.*

### 4. Khởi chạy ứng dụng
Chạy server backend bằng lệnh:
```bash
python backend.py
```
Sau khi server khởi động thành công, mở trình duyệt và truy cập vào:  
👉 **http://127.0.0.1:5000** (hoặc cổng tương ứng hiển thị trên Terminal).

## 📁 Cấu trúc thư mục chính
- `backend.py`: Chứa mã nguồn Flask server và định nghĩa các API (Upload, Generate,...).
- `database.py`: Chứa các hàm giao tiếp trực tiếp với MongoDB (CRUD, chống trùng lặp).
- `questions.py`: Định nghĩa `class Question`, các hàm xử lý đọc file (JSON, DOCX, XLSX), thuật toán xáo trộn đề (`mix_questions`), và xuất file DOCX.
- `index.html`: Giao diện người dùng của ứng dụng.
- `.env`: Cấu hình môi trường (ẩn).
- `Bao_Cao_Do_An.md`: File báo cáo chi tiết quá trình thực hiện đồ án.

## 👤 Tác giả
- Nguyễn Hoàng Tuấn

---
*Ghi chú: Nếu file Word đầu vào gặp lỗi không đọc được, hãy đảm bảo rằng định dạng câu hỏi trong file tuân theo đúng cấu trúc cơ bản có các lựa chọn A, B, C, D rõ ràng.*
