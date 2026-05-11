# BÁO CÁO ĐỒ ÁN MÔN HỌC IT003

## 1. Giới thiệu đồ án
### a. Mô tả chung về ứng dụng
Hệ thống là một ứng dụng Web (Web Application) quản lý ngân hàng câu hỏi trắc nghiệm và hỗ trợ tính năng tự động sinh đề thi. Ứng dụng cung cấp các tính năng nổi bật:
- **Cập nhật ngân hàng câu hỏi đa định dạng**: Hỗ trợ người dùng (giáo viên/quản trị viên) thêm câu hỏi vào hệ thống thông qua nhiều nguồn file khác nhau như JSON, Excel (`.xlsx`) và Word (`.docx`).
- **Quản lý tập trung qua Cơ sở dữ liệu**: Tích hợp **MongoDB** để lưu trữ dữ liệu tập trung, hỗ trợ cả hai chế độ là ghi đè toàn bộ hoặc thêm mới câu hỏi, có khả năng lọc bỏ các câu hỏi trùng lặp khi nhập liệu.
- **Sinh đề thi tự động**: Chức năng cốt lõi cho phép người dùng chỉ định số lượng mã đề cần tạo. Hệ thống sẽ lấy các câu hỏi từ Database, tiến hành xáo trộn thứ tự câu hỏi và thứ tự các đáp án (A, B, C, D) một cách ngẫu nhiên để tạo ra các mã đề khác biệt.
- **Trích xuất hàng loạt**: Đề thi sau khi sinh sẽ được xuất ra dưới dạng các tệp văn bản Word (`.docx`) và nén gọn thành một tệp ZIP duy nhất để người dùng tải xuống nhanh chóng.

### b. Các CTDL và giải thuật đã được sử dụng
**Về Cấu trúc dữ liệu (Data Structures):**
- **Lớp (Class) `Question`**: Được sử dụng để đóng gói toàn bộ thông tin của một câu hỏi trắc nghiệm thành một đối tượng độc lập. Mỗi đối tượng bao gồm: `id`, nội dung câu hỏi (`question`), tập hợp lựa chọn (`options`), đáp án đúng (`answer`), mức độ (`difficulty`), và chủ đề (`topic`).
  👉 *Tại sao (Why)?* Việc áp dụng Lập trình Hướng đối tượng (OOP) giúp dữ liệu có cấu trúc chặt chẽ, dễ dàng truy xuất, đồng thời hỗ trợ các phương thức tự động chuyển đổi định dạng (ví dụ `to_dict`, `from_dict`) để tương tác mượt mà với MongoDB.
- **Cấu trúc Dictionary (Hash Map)**: Dùng để lưu trữ 4 lựa chọn đáp án (A, B, C, D) bên trong lớp `Question`. 
  👉 *Tại sao (Why)?* Cấu trúc Dictionary cho phép tìm kiếm và truy xuất giá trị của một đáp án cụ thể cực kỳ nhanh chóng với độ phức tạp $O(1)$. Nó rất thuận tiện khi cần hoán vị (xáo trộn) giá trị của các đáp án nhưng vẫn cần truy vết xem đâu là đáp án đúng cuối cùng.
- **Cấu trúc Mảng / Danh sách (List)**: Dùng để chứa danh sách toàn bộ các câu hỏi đọc được từ file hoặc từ Database.
  👉 *Tại sao (Why)?* List là cấu trúc tối ưu cho các thao tác duyệt (iteration), lặp tuần tự để xuất file, cũng như để lấy các mẫu ngẫu nhiên (sampling).

**Về Giải thuật (Algorithms):**
- **Giải thuật Trộn ngẫu nhiên (Fisher-Yates Shuffle)**: Ứng dụng thông qua hàm `random.shuffle()` và `random.sample()` tích hợp sẵn trong Python. Giải thuật này được áp dụng vào hai bước: (1) Trộn vị trí các câu hỏi trong đề thi; (2) Trộn vị trí các lựa chọn đáp án (A, B, C, D) trong nội bộ một câu hỏi.
  👉 *Tại sao (Why)?* Fisher-Yates giúp đảm bảo mọi hoán vị đều có xác suất xảy ra bằng nhau với độ phức tạp thời gian cực tốt là $O(n)$, mang lại kết quả xáo trộn công bằng, không thiên lệch thuật toán, tối ưu tài nguyên tính toán.
- **Thuật toán Phân tích cú pháp bằng Regex (Regular Expression)**: Áp dụng để quét và bóc tách dữ liệu văn bản thuần tuý (plain text) từ các file Word tải lên.
  👉 *Tại sao (Why)?* Đề thi định dạng Word thường không có cấu trúc cố định tuyệt đối (VD: có người viết `Câu 1:`, có người viết `Bài 1.`, có người gõ đáp án `A/`, `A)`...). Regex cung cấp khả năng nhận diện mẫu văn bản (pattern matching) vô cùng linh hoạt và mạnh mẽ, giải quyết triệt để sự không đồng nhất về mặt định dạng, giúp hệ thống thông minh hơn.

---

## 2. Quá trình thực hiện
### a. Tuần 1: Khởi tạo kiến trúc và Cấu trúc dữ liệu
- Phân tích yêu cầu bài toán và thiết kế kiến trúc hệ thống.
- Định nghĩa các cấu trúc dữ liệu cốt lõi (`class Question`) để đóng gói thông tin câu hỏi.
- Xây dựng mảng tĩnh (mock data) và thử nghiệm các hàm đọc/ghi cơ bản.

### b. Tuần 2: Hoàn thiện Logic Trộn Đề & Tích hợp MongoDB
- Phát triển module `questions.py` xử lý logic trộn đề căn bản: Áp dụng thuật toán Fisher-Yates để lấy mẫu ngẫu nhiên và xáo trộn vị trí câu hỏi lẫn thứ tự đáp án một cách công bằng.
- Tích hợp thư viện `python-docx` để xây dựng chức năng xuất mảng đối tượng `Question` thành định dạng file Word hoàn chỉnh.
- Xây dựng module `database.py`, kết nối với cơ sở dữ liệu NoSQL **MongoDB**. Cài đặt các hàm thao tác CRUD căn bản (đọc, ghi đè toàn bộ, và nối thêm dữ liệu).

### c. Tuần 3: Xây dựng Backend API & Đa dạng hoá Đầu vào
- Triển khai Flask (`backend.py`) để xây dựng các RESTful API làm cầu nối giao tiếp.
- Xây dựng logic phân tích (parsing) đa định dạng đầu vào. Tích hợp thư viện `pandas` để đọc file Excel (`.xlsx`).
- Xây dựng thuật toán quét và xử lý Regex trên các dòng văn bản để "đọc hiểu" file Word (`.docx`), bất chấp các thói quen gõ khác nhau của giáo viên.
- Cài đặt thuật toán kiểm tra sự tồn tại của câu hỏi (chống trùng lặp nội dung) khi đẩy dữ liệu lên Database.

### d. Tuần 4: Thiết kế Giao diện (Frontend) & Tối ưu luồng xuất
- Phát triển Giao diện người dùng (`index.html`) sử dụng thư viện Tailwind CSS tạo ra một trang Dashboard hiện đại. Tích hợp tính năng upload file bất đồng bộ (fetch/AJAX), hiển thị loader vòng xoay chờ đợi.
- Nâng cấp luồng xuất đề thi: Thay vì lưu các file rác trên ổ cứng máy chủ, hệ thống được tối ưu để sử dụng RAM bộ nhớ tạm (`io.BytesIO()`) để tạo và nén hàng loạt file Word thành một tệp ZIP.
- Gửi luồng dữ liệu (Stream) trực tiếp cho trình duyệt tải xuống, hoàn thiện quy trình sinh đề thi bảo mật và tốc độ cao.

---

## 3. Kết quả đạt được
- Xây dựng thành công một ứng dụng web hoàn chỉnh, tự động hóa quy trình quản lý và tạo đề thi trắc nghiệm.
- Xử lý mượt mà và linh hoạt các định dạng dữ liệu đầu vào (đặc biệt là khả năng "đọc hiểu" file Word không theo quy chuẩn cứng nhắc).
- Giao tiếp Database ổn định, loại bỏ triệt để các câu hỏi bị lặp lại nội dung.
- Giao diện trực quan, dễ sử dụng. Thuật toán trộn đề chạy đúng nghiệp vụ: sinh ra các đề thi khác biệt mà vẫn đảm bảo tính chính xác của đáp án được trộn đi kèm.

---

## 4. Tài liệu tham khảo
- Python 3.x Documentation (Các module chuẩn: `json`, `random`, `re`, `io`, `zipfile`).
- Tài liệu Flask Framework (https://flask.palletsprojects.com/).
- PyMongo Documentation (Tài liệu kết nối MongoDB).
- Thư viện python-docx (https://python-docx.readthedocs.io/).
- Thư viện Pandas (https://pandas.pydata.org/).
- Tailwind CSS Framework (https://tailwindcss.com/).

---

## 5. Phụ lục 1: Giới thiệu (demo) kết quả
*(Ghi chú cho sinh viên: Bạn cần chụp ảnh màn hình máy tính của mình và dán đè vào mục này trước khi nộp)*
- **Hình 1**: Giao diện chính của ứng dụng trên trình duyệt web, hiển thị các khu vực Upload file và khu vực Cấu hình sinh đề thi.
- **Hình 2**: Ảnh chụp kết quả màn hình thông báo "Tải lên thành công" khi import file Word mẫu.
- **Hình 3**: Giao diện của MongoDB Compass hiển thị các Documents câu hỏi đã được lưu trữ thành công vào Database.
- **Hình 4**: Cấu trúc file `.zip` tải xuống chứa nhiều mã đề (VD: `IT003_De_001.docx`, `IT003_De_002.docx`).
- **Hình 5**: So sánh 2 file mã đề Word được sinh ra để thấy sự khác biệt về vị trí câu hỏi và vị trí đáp án.

---

## 6. Phụ lục 2: Docstring (Mô tả hàm)
Dưới đây là mô tả logic chức năng cho một số module cốt lõi của hệ thống:

- **`class Question`**: Lớp mô hình hoá dữ liệu câu hỏi trắc nghiệm. Khởi tạo đối tượng bao gồm ID, text nội dung, dict chứa 4 đáp án, đáp án đúng, độ khó và chủ đề. Chứa các hàm `to_dict` và `from_dict` hỗ trợ Serialize/Deserialize dữ liệu với JSON và MongoDB.
- **`mix_questions(questionset)`**: Hàm nhận đầu vào là mảng các `Question`. Quy trình: Nhóm câu hỏi theo độ khó -> Sử dụng `random.sample` để lấy câu hỏi ngẫu nhiên -> Gộp lại và dùng `random.shuffle` để xáo trộn tổng thể toàn bộ mảng. Trong nội bộ mỗi đối tượng câu hỏi, tiếp tục sử dụng thuật toán xáo trộn để hoán vị các tuỳ chọn A,B,C,D. Trả về một mảng câu hỏi mới đã được trộn hoàn toàn.
- **`export_questions_to_docx(questions, exam_code, filename)`**: Nhận mảng đối tượng `Question` đã trộn. Khởi tạo một đối tượng văn bản `Document` mới. Lặp qua danh sách và gọi các phương thức `add_paragraph()` để ghi nội dung câu hỏi và các đáp án A, B, C, D theo đúng định dạng. Lưu kết quả ra file bộ nhớ.
- **`append_questions_to_mongodb(questions)`**: Hàm bổ trợ DB. Sử dụng Set (`{}`) để lưu trữ nhanh các đoạn text nội dung (đã lowercase và strip) của các câu hỏi hiện có dưới CSDL. Duyệt qua danh sách câu hỏi tải lên, nếu câu hỏi nào có nội dung chưa từng xuất hiện trong Set thì mới được đưa vào danh sách chèn (insert).
- **`@app.route('/api/generate-exams', methods=['POST'])`**: Endpoint API cốt lõi nhận yêu cầu tạo đề. Kéo mảng toàn bộ dữ liệu từ MongoDB. Chạy vòng lặp $N$ lần (tương ứng $N$ số lượng mã đề yêu cầu) -> Gọi hàm `mix_questions()` -> Gọi `export_questions_to_docx` lưu vào vùng đệm `io.BytesIO()` -> Ghi đệm vào đối tượng nén `zipfile`. Cuối cùng dùng `send_file` trả về file `.zip` cho HTTP Response.
