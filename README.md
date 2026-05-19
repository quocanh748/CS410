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

### HƯỚNG DẪN CHẠY DEMO

1. Yêu cầu hệ thống & Cài đặt thư viện

Trước khi chạy, hãy đảm bảo bạn đã cài đặt Python (khuyến nghị phiên bản 3.8 trở lên). Sau đó, cài đặt các thư viện cần thiết bằng lệnh sau:

```bash
pip install -r requirements.txt
```

*Lưu ý: Nếu bạn sử dụng mô hình local qua Ollama (như mặc định trong code là `qwen2.5:1.5b`), hãy đảm bảo bạn đã cài đặt Ollama và tải model về máy.*

2. Cấu trúc thư mục
Dự án có cấu trúc chính như sau:
```text
├── pb/                  # Thư mục chứa logic lõi của thuật toán
├── main.py              # File chạy ứng dụng bằng dòng lệnh (CLI)
├── sl_main.py           # File chạy giao diện web (Streamlit)
└── requirements.txt     # Danh sách thư viện
```

3. Khởi chạy Ứng dụng

**Cách 1: Chạy giao diện Web (Streamlit)**
Đây là cách dễ nhất để tương tác và theo dõi thuật toán trực quan.
```bash
streamlit run sl_main.py
```
Sau khi chạy thành công, mở trình duyệt web và truy cập vào đường dẫn hiển thị trên terminal (thường là `http://localhost:8501`).

**Cách 2: Chạy trực tiếp qua dòng lệnh (CLI)**
```bash
python main.py
```
Bạn có thể tùy chỉnh các tham số như số lượng đột biến, số thế hệ... bằng cách truyền tham số (ví dụ: `python main.py -mp 2 -ts 4`). Xem thêm chi tiết trong file `main.py`.
