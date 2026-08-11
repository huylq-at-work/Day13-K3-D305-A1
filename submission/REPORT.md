# Báo cáo Day 13 Observability

## 1. Thông tin nhóm

- Tên nhóm:
- Repository URL:
- Commit SHA cuối:
- Thành viên và vai trò: Nguyễn Chí Hướng — 2A202601203 — Logging & PII

## 2. Kết quả kỹ thuật

- Điểm `validate_logs.py`: 100/100
- Tổng số traces:
- Số PII leak còn lại: 0 trong 21 log records của Checkpoint 1
- Link/đường dẫn dashboard:

## 3. Logging và tracing

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
| Nguyễn Chí Hướng — 2A202601203 | Correlation ID middleware; JSON log enrichment; hash user ID; PII redaction; tests và evidence Checkpoint 1 | Branch `logging-and-pii` (điền commit SHA sau khi commit) | Correlation ID cần được validate/propagate xuyên suốt request; PII phải được scrub ở processor cuối trước khi render JSON. |
