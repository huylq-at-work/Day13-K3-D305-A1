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
- Link/đường dẫn dashboard: `scripts/dashboard.py` (Local Streamlit app)

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
- Evidence dashboard: Đã lưu ảnh chụp giao diện khi ứng dụng chạy vào `submission/evidence/dashboard_runtime.png` *(bạn nhớ tự chụp ảnh và lưu file này nhé)*.
- SLO đã chọn và lý do: Dựa theo `config/dashboard.yaml`, SLO **Latency P95 <= 3000ms**. Lý do: Với ứng dụng Chat AI, nếu chờ quá 3 giây trải nghiệm người dùng sẽ rất tệ; 95% lượng request buộc phải trả về kết quả dưới ngưỡng này để đảm bảo chất lượng dịch vụ.
- Alert rules và runbook:
  - **Alert rules**: Kích hoạt khi *P95 Latency > 3000ms* trong 1 phút (hoặc Error Rate > 2%).
  - **Runbook**: (1) Kiểm tra panel Errors xem có lỗi phát sinh nội bộ không. (2) Nếu error rate = 0 nhưng latency cao, mở Traces/Logs tìm `correlation_id` của request chậm nhất. (3) Khoanh vùng span tốn thời gian (thường là Agent/Retrieval) để xác định nghẽn cổ chai và áp dụng fix (ví dụ: timeout).

## 6. Điều tra challenge

> Bằng chứng đầy đủ: [evidence/challenge/NOTES.md](evidence/challenge/NOTES.md).
> Diễn tập trước đó: [evidence/practice_rag_slow/NOTES.md](evidence/practice_rag_slow/NOTES.md).

- Challenge ID: `day13-k3-observability-v1` (incident `rag_slow`, feature `refund`,
  `latency_threshold_ms` = 2000)
- Triệu chứng từ metrics: p95/p99 tăng **151ms → 2651ms**, vượt threshold 2000ms;
  error rate = 0, cost và token không đổi → sự cố latency thuần. p50 tổng vẫn 150ms
  vì chỉ 5/15 request thuộc feature `refund`.
  ([01_metrics_before.json](evidence/challenge/01_metrics_before.json) ↔
  [04_metrics_during.json](evidence/challenge/04_metrics_during.json))
- Trace ID liên quan: _(chưa có — lần chạy này `tracing_enabled: false` vì thiếu
  Langfuse key; R2 bổ sung trace waterfall của span retrieval)_
- Log line/correlation ID liên quan: `req-714561b0`
  ([05_logs_by_correlation_id.jsonl](evidence/challenge/05_logs_by_correlation_id.jsonl));
  toàn bộ 5 request `refund` trong
  [06_all_refund_response_logs.jsonl](evidence/challenge/06_all_refund_response_logs.jsonl)
- Root cause: bước retrieval của RAG chậm thêm ~2.5s mỗi request
  (`app/mock_rag.py:18` — `time.sleep(2.5)` khi flag `rag_slow` bật), tự nó đã vượt SLO.
  **Nghiêm trọng hơn**: lệnh sleep đồng bộ này nằm trong endpoint `async def`
  (`app/main.py:46`) nên khoá event loop, khiến các request đồng thời bị xếp hàng —
  log cho thấy 5 request gửi cùng lúc nhưng response cách nhau đúng ~2.65s, và client
  đo **13301ms** trong khi server chỉ ghi `latency_ms: 2650`. Metrics đang under-report
  latency thật vì chỉ đo `agent.run()`, không tính thời gian chờ hàng đợi.
- Fix action: (1) timeout ~500ms cho retrieval kèm fallback trả lời không có context;
  (2) đưa lời gọi chặn ra khỏi event loop (`run_in_threadpool` hoặc để `/chat` là `def`
  thường); (3) đo `latency_ms` từ middleware để phản ánh đúng trải nghiệm người dùng.
- Preventive measure: alert p95 **tách theo `feature`** (p50 tổng che mất sự cố của
  `refund`); alert trên chênh lệch client-latency vs server-`latency_ms` như dấu hiệu
  sớm của xếp hàng; quy ước review code cấm gọi hàm chặn trong endpoint `async`; load
  test định kỳ với `--concurrency > 1` vì chạy tuần tự không bao giờ lộ lỗi này.

## 7. Đóng góp cá nhân

Với mỗi thành viên, ghi rõ nhiệm vụ và link commit/PR tương ứng.

| Thành viên | Phần việc | Commit/PR | Điều đã học |
|---|---|---|---|
| Nguyễn Chí Hướng — 2A202601203 | Correlation ID middleware; JSON log enrichment; hash user ID; PII redaction; tests và evidence Checkpoint 1 | `5d55476` | Correlation ID cần được validate/propagate xuyên suốt request; PII phải được scrub ở processor cuối trước khi render JSON. |
| Phạm Thị Liên — 2A202601795 | Role 2 — tracing, prompt v1/v2, label/rollback | | |
| Nguyễn Tiến Đạt — 2A202601387 | Role 3 — dashboard 6 panel, SLO, alert, runbook | `fc1d31b` | Hiểu rõ cách trực quan hóa dữ liệu từ Log thành Dashboard; nắm được tầm quan trọng của SLO và việc gắn metrics với ngữ cảnh người dùng. |
| Lê Quang Huy — 2A202601821 | Role 4 — setup baseline, practice + challenge incident, report, demo | `0cf830e`, `1ed3698` | Metrics chỉ nói "có sự cố", trace nói "chậm ở đâu", log mới chứng minh được nguyên nhân — thiếu một tầng là mất bằng chứng. |
