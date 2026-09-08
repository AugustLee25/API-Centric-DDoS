# 🛡️ API-Centric DDoS & Resource Exhaustion Simulation Lab

> ⚠️ **DISCLAIMER (CẢNH BÁO)**
> **CHỈ SỬ DỤNG CHO MỤC ĐÍCH HỌC TẬP VÀ NGHIÊN CỨU.** Việc thực hiện các cuộc tấn công DDoS vào các hệ thống mà bạn không sở hữu hoặc không có sự cho phép là **BẤT HỢP PHÁP**. Tác giả không chịu trách nhiệm về bất kỳ hành vi sử dụng công cụ này cho mục đích xấu nào.

---

## 📖 Giới thiệu (Introduction)

Dự án này mô phỏng các kỹ thuật tấn công DDoS (Distributed Denial of Service) tập trung vào tầng ứng dụng (Layer 7), cụ thể là các cuộc tấn công vào API để gây ra tình trạng cạn kiệt tài nguyên (Resource Exhaustion). 

Thay vì chỉ tấn công bằng băng thông (Volumetric), dự án tập trung vào việc khai thác các lỗ hổng về logic xử lý của server thông qua các request phức tạp, chiếm dụng kết nối và làm quá tải tài nguyên tính toán (CPU/RAM).

---

## 🎯 Mục tiêu nghiên cứu (Research Objectives)

- **Mô phỏng tấn công Slow HTTP/POST:** Giữ kết nối mở lâu nhất có thể để chiếm dụng Connection Pool.
- **Tấn công Payload nặng (Heavy Payload):** Gửi các cấu trúc dữ liệu lớn (Large JSON, Nested Objects) để gây áp lực lên CPU (Parsing) và RAM (Memory Allocation).
- **Tìm ra giới hạn chịu tải (Breaking Point):** Xác định ngưỡng mà tại đó server bắt đầu bị nghẽn (Latency tăng) và sụp đổ (Timeout/Connection Refused).

---

## 🛠️ Kỹ thuật mô phỏng (Methodology)

Dự án sử dụng thư viện `asyncio` và `aiohttp` để thực hiện tấn công bất đồng bộ, cho phép mô phỏng hàng nghìn kết nối đồng thời với hiệu suất cao.

### 🚀 Các chiến thuật tấn công được áp dụng:

1. **Connection Exhaustion:** Sử dụng số lượng kết nối đồng thời cực lớn (`MAX_CONCURRENT_CONNECTIONS`) để làm cạn kiệt khả năng tiếp nhận của Web Server.
2. **Resource Exhaustion (CPU/RAM):**
   - Gửi các request POST với payload JSON lớn và cấu trúc lồng nhau (Nested).
   - Sử dụng dữ liệu ngẫu nhiên để tránh cơ chế Cache của server.
3. **Slow-Rate Attack:** Giữ các kết nối mở lâu nhất có thể bằng cách gửi dữ liệu chậm hoặc duy trì kết nối để chiếm dụng socket.

---

## 📊 Kết quả thực nghiệm (Experimental Results)

Trong quá trình mô phỏng trên môi trường Lab, các chỉ số sau đã được quan sát:

| Chỉ số | Trạng thái bình thường | Trạng thái bị tấn công (Breaking Point) |
| :--- | :--- | :--- |
| **RPS (Requests Per Second)** | Cao & Ổn định | Giảm mạnh (từ ~2000 xuống < 800) |
| **Latency (Độ trễ)** | Thấp (< 0.1s) | Tăng vọt (Gây ra Timeout) |
| **Success Rate** | ~100% | Giảm dần về 0% |
| **Timeouts** | Gần như bằng 0 | Tăng vọt (Chiếm đa số trong các request) |
| **Error Type** | Không có | `TimeoutError`, `ConnectionRefused` |

### 📈 Biểu đồ quan sát (Observation Log)

- **Giai đoạn 1:** Server phản hồi nhanh, lỗi 404/405 (do sai endpoint).
- **Giai đoạn 2:** Server bắt đầu xử lý chậm, Timeouts xuất hiện rải rác.
- **Giai đoạn 3 (Critical):** Timeouts chiếm tỷ lệ áp đảo (>90%), RPS giảm mạnh, server rơi vào trạng thái tê liệt hoàn toàn.

---

## 🛡️ Giải pháp phòng thủ đề xuất (Mitigation Strategies)

Dựa trên kết quả thực nghiệm, các giải pháp sau được đề xuất để bảo vệ hệ thống:

- **Rate Limiting:** Giới hạn số lượng request từ một IP trong một khoảng thời gian nhất định.
- **WAF (Web Application Firewall):** Sử dụng WAF để nhận diện và chặn các payload bất thường hoặc các pattern tấn công Layer 7.
- **Connection Management:** Cấu hình giới hạn số lượng kết nối đồng thời (Max Connections) và thời gian timeout của socket.
- **Auto-scaling:** Sử dụng kiến trúc Cloud để tự động mở rộng tài nguyên khi phát hiện tải tăng đột biến.
- **Payload Validation:** Kiểm tra kích thước và cấu trúc dữ liệu đầu vào ngay tại tầng Gateway để tránh xử lý các payload quá lớn.

---

## 📝 Hướng dẫn sử dụng (Usage)

Thực hiện các lệnh sau trong terminal để chạy môi trường lab:

```bash
# 1. Clone repository
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name

# 2. Cài đặt thư viện
pip install aiohttp

# 3. Cấu hình target (Chỉnh sửa TARGET_URL trong file test.py nếu cần)

# 4. Chạy mô phỏng
python test.py
```

---
*Dự án được thực hiện bởi **[Tên của bạn]** nhằm mục đích nghiên cứu Cybersecurity.*
