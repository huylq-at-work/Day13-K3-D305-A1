# Template Alert và Runbook

Mỗi alert phải dựa trên triệu chứng người dùng hoặc SLO, không dựa trực tiếp vào tên implementation nội bộ.

## Alert 1

- Tên: High Latency Alert (Độ trễ cao)
- Severity: High (Nghiêm trọng)
- SLI/SLO liên quan: P95 Latency <= 3000ms
- Điều kiện và thời gian duy trì: P95 Latency > 3000ms duy trì liên tục trong 1 phút.
- Ảnh hưởng tới người dùng: Người dùng phải chờ rất lâu mới nhận được phản hồi chat, gây ức chế và giảm tương tác.
- Ba bước kiểm tra đầu tiên: (1) Kiểm tra panel Error xem có lỗi đồng thời không. (2) Mở Langfuse lấy Trace của request chậm nhất. (3) Khoanh vùng xem span nào (Retrieval hay LLM) tốn nhiều thời gian nhất.
- Mitigation tạm thời: Giảm timeout của bước Retrieval hoặc tạm thời trả về câu trả lời fallback (không dùng context) để cứu vớt trải nghiệm.
- Owner: Nguyễn Tiến Đạt (Role 3)

## Alert 2

- Tên: High Error Rate Alert (Tỷ lệ lỗi cao)
- Severity: Critical (Cấp cứu)
- SLI/SLO liên quan: Error Rate < 2%
- Điều kiện và thời gian duy trì: Error rate > 2% duy trì trong 1 phút.
- Ảnh hưởng tới người dùng: Người dùng liên tục nhận được thông báo lỗi, không thể sử dụng tính năng.
- Ba bước kiểm tra đầu tiên: (1) Xem breakdown error type trên dashboard để biết loại lỗi. (2) Mở file `data/logs.jsonl` tìm `correlation_id` lỗi để đọc traceback. (3) Kiểm tra trạng thái của các dịch vụ bên thứ 3 (như OpenAI/Claude API).
- Mitigation tạm thời: Tắt tính năng đang lỗi hoặc chuyển (fallback) sang model dự phòng (ví dụ: chuyển từ GPT-4 sang GPT-3.5).
- Owner: Nguyễn Tiến Đạt (Role 3)

## Alert 3

- Tên: Low Quality Score Alert (Chất lượng phản hồi kém)
- Severity: Medium (Trung bình)
- SLI/SLO liên quan: Mean Quality Score >= 3.5
- Điều kiện và thời gian duy trì: Quality Score trung bình < 3.5 duy trì trong 5 phút.
- Ảnh hưởng tới người dùng: Chatbot trả lời sai lệch hoặc thiếu thông tin, dẫn tới trải nghiệm tồi.
- Ba bước kiểm tra đầu tiên: (1) Lọc các log có điểm Quality thấp. (2) Đọc kỹ user prompt và response xem AI trả lời sai do thiếu context hay do prompt. (3) Rollback về prompt version cũ trên Langfuse nếu version mới bị lỗi.
- Mitigation tạm thời: Nhanh chóng đổi label prompt trên Langfuse để quay về version ổn định (rollback).
- Owner: Phạm Thị Liên (Role 2) / Nguyễn Tiến Đạt (Role 3)
