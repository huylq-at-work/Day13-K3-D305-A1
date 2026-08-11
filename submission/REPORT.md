# Báo cáo Day 13 Observability

## 1. Thông tin nhóm

- Tên nhóm:
- Repository URL:
- Commit SHA cuối:
- Thành viên và vai trò:
  - Nguyễn Chí Hướng — 2A202601203 — Logging & PII
  - Liên — Tracing & Prompt Version

## 2. Kết quả kỹ thuật

- Điểm `validate_logs.py`: 100/100
- Tổng số traces: 10 traces CP2 Role 2 có metadata trên Langfuse
- Số PII leak còn lại: 0 trong 21 log records của Checkpoint 1
- Link/đường dẫn dashboard:

## 3. Logging và tracing

- Evidence correlation ID: [`evidence/checkpoint-1-logging-pii.md`](evidence/checkpoint-1-logging-pii.md)
- Evidence PII redaction: [`evidence/checkpoint-1-logging-pii.md`](evidence/checkpoint-1-logging-pii.md)
- Evidence trace waterfall: [`evidence/checkpoint-2-tracing-prompt-versioning.md`](evidence/checkpoint-2-tracing-prompt-versioning.md)
- Giải thích một span đáng chú ý: Span `run` liên kết generation với managed prompt. Metadata có `prompt_name`, `prompt_label`, `prompt_version`, `prompt_source`, `doc_count` và `query_preview`, giúp truy ngược request đã dùng prompt version nào.

## 4. Prompt versioning

- Prompt name: `day13-chat`
- Version/label baseline: version 1, labels `baseline` và `production`
- Version/label candidate: version 2, label `candidate`
- Trace ID của mỗi version:
  - baseline v1: `7e89ea3111f42b814ad5b735b07d2f5f`
  - candidate v2: `fc60baea1602e9759d9807b9bcd15a01`
  - production sau rollback về v1: `bd16ddb65d4569681c162a85717e1023`
- Bằng chứng đổi label hoặc rollback: [`evidence/checkpoint-2-tracing-prompt-versioning.md`](evidence/checkpoint-2-tracing-prompt-versioning.md)

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
| Liên | Tracing; Langfuse prompt `day13-chat`; prompt v1/v2; label switch/rollback; trace metadata evidence Checkpoint 2 | Branch/commit SHA sau khi commit | Trace metadata phải gắn prompt name, label và version để truy ngược request đã dùng prompt nào. |
