# Báo cáo Day 13 Observability

## 1. Thông tin nhóm

- Tên nhóm: D305 (cohort K3, đề A1)
- Repository URL: https://github.com/huylq-at-work/Day13-K3-D305-A1
- Commit SHA cuối: _(điền lúc nộp — lấy bằng `git rev-parse HEAD`)_
- Thành viên và vai trò:
  - Nguyễn Chí Hướng — 2A202601203 — Role 1: Logging & PII
  - Phạm Thị Liên — 2A202601795 — Role 2: Tracing & Prompt Version
  - Nguyễn Tiến Đạt — 2A202601387 — Role 3: Dashboard, SLO & Alert
  - Lê Quang Huy — 2A202601821 — Role 4: Incident, Report & Demo

## 2. Kết quả kỹ thuật

- Điểm `validate_logs.py`: baseline **30/100** lúc setup
  ([cp0_baseline_validate_logs.txt](evidence/cp0_baseline_validate_logs.txt))
  → sau Checkpoint 1 đạt **100/100**
  ([checkpoint-1-validate-logs.txt](evidence/checkpoint-1-validate-logs.txt))
- Tổng số traces: _(R2 điền — tối thiểu 10)_
- Số PII leak còn lại: 0 trong 21 log records của Checkpoint 1
- Link/đường dẫn dashboard: _(R3 điền)_

## 3. Logging và tracing

- Evidence correlation ID: [`evidence/checkpoint-1-logging-pii.md`](evidence/checkpoint-1-logging-pii.md)
- Evidence PII redaction: [`evidence/checkpoint-1-logging-pii.md`](evidence/checkpoint-1-logging-pii.md)
- Evidence trace waterfall: _(R2)_
- Giải thích một span đáng chú ý: _(R2)_

## 4. Prompt versioning

- Prompt name: `day13-chat`
- Version/label baseline: _(R2)_
- Version/label candidate: _(R2)_
- Trace ID của mỗi version: _(R2)_
- Bằng chứng đổi label hoặc rollback: _(R2)_

## 5. Dashboard, SLO và alerts

- Kết quả `validate_dashboard.py`: `HỢP LỆ: 6/6 panel` từ baseline (xem
  [cp0_baseline_validate_logs.txt](evidence/cp0_baseline_validate_logs.txt));
  _(R3 chụp lại kèm ảnh dashboard runtime)_
- Evidence dashboard: _(R3)_
- SLO đã chọn và lý do: _(R3)_
- Alert rules và runbook: _(R3)_

## 6. Điều tra challenge

> Đã diễn tập quy trình với practice scenario cùng loại — xem
> [evidence/practice_rag_slow/NOTES.md](evidence/practice_rag_slow/NOTES.md).
> Số liệu chính thức dưới đây sẽ chạy trên `main` sau khi R2–R3 merge.

- Challenge ID: `day13-k3-observability-v1` (incident `rag_slow`, feature `refund`,
  threshold 2000ms)
- Triệu chứng từ metrics: _(chạy chính thức — practice cho thấy p95 tăng
  151ms → 2651ms, không error, cost không đổi)_
- Trace ID liên quan: _(điền sau khi chạy chính thức, cần R2 + Langfuse key)_
- Log line/correlation ID liên quan: _(điền sau khi chạy chính thức)_
- Root cause: _(dự kiến từ practice: bước retrieval của RAG bị chậm ~2.5s/request —
  flag `rag_slow` kích hoạt `time.sleep(2.5)` trong `app/mock_rag.py`, mô phỏng
  vector store chậm; xác nhận lại bằng trace + log chính thức)_
- Fix action: _(điền sau khi chạy chính thức)_
- Preventive measure: _(điền sau khi chạy chính thức)_

## 7. Đóng góp cá nhân

Với mỗi thành viên, ghi rõ nhiệm vụ và link commit/PR tương ứng.

| Thành viên | Phần việc | Commit/PR | Điều đã học |
|---|---|---|---|
| Nguyễn Chí Hướng — 2A202601203 | Correlation ID middleware; JSON log enrichment; hash user ID; PII redaction; tests và evidence Checkpoint 1 | `5d55476` | Correlation ID cần được validate/propagate xuyên suốt request; PII phải được scrub ở processor cuối trước khi render JSON. |
| Phạm Thị Liên — 2A202601795 | Role 2 — tracing, prompt v1/v2, label/rollback | | |
| Nguyễn Tiến Đạt — 2A202601387 | Role 3 — dashboard 6 panel, SLO, alert, runbook | | |
| Lê Quang Huy — 2A202601821 | Role 4 — setup baseline, practice + challenge incident, report, demo | `0cf830e`, `1ed3698` | Metrics chỉ nói "có sự cố", trace nói "chậm ở đâu", log mới chứng minh được nguyên nhân — thiếu một tầng là mất bằng chứng. |
