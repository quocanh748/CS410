this repo based on :https://github.com/vaughanlove/PromptBreeder.git
for study dont sue us

<!-- Banner -->
<p align="center">
  <a href="https://www.uit.edu.vn/" title="Trường Đại học Công nghệ Thông tin" style="border: none;">
    <img src="https://i.imgur.com/WmMnSRt.png" alt="Trường Đại học Công nghệ Thông tin | University of Information Technology">
  </a>
</p>

<h1 align="center"><b>Mạng neural và thuật giải di truyền</b></h>
<h2 align="center"><b>Promptbreeder: Self-Referential Self-Improvement via Prompt Evolution</b></h>

## THÀNH VIÊN NHÓM 1
| STT    | MSSV          | Họ và Tên              
| ------ |:-------------:| ----------------------
| 1      | 23520070      | Phạm Ngô Quốc Anh      
| 2      | 23520514      | Đoàn Thái Hoàng       
| 3      | 23520021      | Nguyễn Tri An       
| 4      | 22521188      | Phạm Phú Minh Quân

## GIỚI THIỆU MÔN HỌC
* **Tên môn học:** Mạng neural và thuật giải di truyền
* **Mã môn học:** CS410.Q21
* **Năm học:** HK2 (2025 - 2026)
* **Giảng viên**: T.S Lương Ngọc Hoàng

### HƯỚNG DẪN CHẠY CHƯƠNG TRÌNH

1. Yêu cầu hệ thống & Cài đặt thư viện

Trước khi chạy, hãy đảm bảo bạn đã cài đặt Python (khuyến nghị phiên bản 3.8 trở lên). Sau đó, cài đặt các thư viện cần thiết bằng lệnh sau:

```bash
pip install -r requirements.txt
```

*Lưu ý: Nếu bạn sử dụng mô hình local qua Ollama (mặc định trong code là `qwen2.5:1.5b`), hãy đảm bảo:*
* Đã cài đặt [Ollama](https://ollama.com/) và ứng dụng đang chạy dưới nền.
* Đã tải mô hình về máy bằng cách mở Terminal/Command Prompt và chạy lệnh sau:
  ```bash
  ollama pull qwen2.5:1.5b
  ```
* (Tùy chọn) Nếu muốn dùng mô hình khác lớn hơn hoặc nhỏ hơn, bạn có thể tải chúng về (ví dụ: `ollama pull llama3`) và cấu hình lại tên mô hình trong giao diện chạy.

2. Cấu trúc thư mục
Dự án có cấu trúc chính như sau:
```text
├── pb/                  # Thư mục chứa logic lõi của thuật toán
├── demo/                # Thư mục chứa ứng dụng demo kết quả đã tiến hóa
│   ├── app.py           # Web app demo so sánh Prompt đã tiến hóa vs Baseline
│   └── ...
├── main.py              # File chạy tiến hóa/đột biến bằng dòng lệnh (CLI)
├── sl_main.py           # File chạy tiến hóa/đột biến qua giao diện web (Streamlit)
└── requirements.txt     # Danh sách thư viện
```

3. Hướng dẫn chạy Đột biến & Tiến hóa Prompt (Mutation & Evolution Loop)

Đây là tiến trình chạy thuật toán PromptBreeder để tìm kiếm và tối ưu hóa các prompt qua nhiều thế hệ tiến hóa đột biến.

**Cách 1: Chạy giao diện Web (Streamlit) - Trực quan nhất**
```bash
streamlit run sl_main.py
```
Sau khi chạy thành công, mở trình duyệt web và truy cập vào địa chỉ hiển thị trên terminal (thường là `http://localhost:8501`). Bạn có thể chọn các phong cách tư duy (T), các câu lệnh đột biến (M), cấu hình số lượng thế hệ và theo dõi biểu đồ phân bố fitness theo thời gian thực.

**Cách 2: Chạy trực tiếp qua dòng lệnh (CLI)**
```bash
python main.py
```
Bạn có thể tùy chỉnh các tham số như số lượng đột biến, số thế hệ... bằng cách truyền tham số (ví dụ: `python main.py -mp 2 -ts 4`). Xem thêm chi tiết trong file `main.py`.

4. Hướng dẫn chạy Demo giải toán (So sánh Prompt đã tiến hóa vs Baseline)

Sau khi quá trình tiến hóa hoàn tất và tìm ra prompt tốt nhất (ở Generation 16 với Fitness đạt 75%), bạn có thể chạy ứng dụng demo để so sánh khả năng giải toán của prompt tối ưu này so với prompt thông thường (Baseline).

**Khởi chạy giao diện Demo:**
```bash
streamlit run demo/app.py
```
Ứng dụng demo cho phép bạn nhập các câu hỏi toán học (hoặc chọn mẫu có sẵn), gửi đồng thời tới Ollama bằng 2 phương pháp (Evolved Prompt vs Baseline) và so sánh trực quan thời gian phản hồi cũng như chất lượng lời giải.
