# Báo cáo Day 13 Observability

## 1. Thông tin nhóm

- Tên nhóm:
- Repository URL:
- Commit SHA cuối:
- Thành viên và vai trò: Nguyễn Chí Hướng — 2A202601203 — Role 1: Logging & PII

## 2. Kết quả kỹ thuật

- Điểm `validate_logs.py`: 100/100
- Kết quả test cho Checkpoint 1: 27 passed
- Số correlation ID duy nhất trong lần kiểm tra: 10
- Tổng số traces:
- Số PII leak còn lại: 0 trong 21 log records của Checkpoint 1
- Link/đường dẫn dashboard:

## 3. Logging và tracing

- Người thực hiện Logging & PII: Nguyễn Chí Hướng — 2A202601203.
- Correlation ID: middleware chấp nhận `x-request-id` hợp lệ theo định dạng
  `req-<8 ký tự hex>`; nếu header thiếu hoặc sai định dạng thì sinh ID mới. ID được
  bind vào request context, dùng chung trong các log API, trả về response body/header
  `x-request-id`, và context được xóa sau request để tránh rò rỉ giữa các request.
- Log enrichment: trước event `request_received`, API bind `user_id_hash`,
  `session_id`, `feature`, `model` và `env`. `user_id` chỉ được ghi dưới dạng SHA-256
  rút gọn, không ghi nguyên văn.
- PII redaction: processor scrub đệ quy chuỗi trong context, payload, list và object
  lồng nhau sau bước render exception/stack nhưng trước khi render và ghi JSONL.
  Email, số điện thoại Việt Nam và số thẻ thử nghiệm được thay bằng placeholder.
- Kiểm thử: bổ sung test cho ID sinh mới/propagation, response headers, metadata,
  user ID hash và redaction email/điện thoại/thẻ trong log thực tế.
- Evidence kết quả validator: [`evidence/checkpoint-1-validate-logs.txt`](evidence/checkpoint-1-validate-logs.txt)
- Evidence correlation ID: [`evidence/checkpoint-1-logging-pii.md`](evidence/checkpoint-1-logging-pii.md)
- Evidence PII redaction: [`evidence/checkpoint-1-logging-pii.md`](evidence/checkpoint-1-logging-pii.md)
- Evidence trace waterfall:
- Giải thích một span đáng chú ý:

## 4. Prompt versioning

- Prompt name:
- Version/label baseline:
- Version/label candidate:
- Trace ID của mỗi version:
- Bằng chứng đổi label hoặc rollback:

## 5. Dashboard, SLO và alerts

- Kết quả `validate_dashboard.py`:
- Evidence dashboard:
- SLO đã chọn và lý do:
- Alert rules và runbook:

## 6. Điều tra challenge

- Challenge ID:
- Triệu chứng từ metrics:
- Trace ID liên quan:
- Log line/correlation ID liên quan:
- Root cause:
- Fix action:
- Preventive measure:

## 7. Đóng góp cá nhân

Với mỗi thành viên, ghi rõ nhiệm vụ và link commit/PR tương ứng.

| Thành viên | Phần việc | Commit/PR | Điều đã học |
|---|---|---|---|
| Nguyễn Chí Hướng — 2A202601203 | Hoàn thiện correlation ID middleware; structured JSON log enrichment; hash user ID; PII redaction đệ quy; tests và evidence Checkpoint 1 | [Commit `5d55476`](https://github.com/huylq-at-work/Day13-K3-D305-A1/commit/5d55476cb72a0ddd8f7782b3a3a764a9a3dc826d) | Hiểu cách validate và propagate correlation ID, cô lập context giữa request, phân biệt hashing với redaction và scrub PII trước khi render JSON. |
