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
- Tổng số traces: **60** trên project Langfuse chung của nhóm — gồm 10 traces
  Checkpoint 2 của R2 (prompt v1/v2, label switch và rollback) và 16 traces Checkpoint 3
  của R4 (traffic nền + 5 trace challenge). Xem
  [checkpoint-2-tracing-prompt-versioning.md](evidence/checkpoint-2-tracing-prompt-versioning.md)
  và [08_langfuse_traces_list.txt](evidence/challenge/08_langfuse_traces_list.txt).
- Số PII leak còn lại: 0 trong 21 log records của Checkpoint 1
- Link/đường dẫn dashboard: _(R3 điền)_

## 3. Logging và tracing

- Evidence correlation ID: [`evidence/checkpoint-1-logging-pii.md`](evidence/checkpoint-1-logging-pii.md)
- Evidence PII redaction: [`evidence/checkpoint-1-logging-pii.md`](evidence/checkpoint-1-logging-pii.md)
- Evidence trace waterfall: ảnh [`evidence/prompt_ver1.jpg`](evidence/prompt_ver1.jpg)
  và [`evidence/prompt_ver2.jpg`](evidence/prompt_ver2.jpg) (cây span kèm metadata);
  dữ liệu trace challenge trong
  [09_trace_detail_slowest.json](evidence/challenge/09_trace_detail_slowest.json) và
  [`evidence/checkpoint-2-tracing-prompt-versioning.md`](evidence/checkpoint-2-tracing-prompt-versioning.md)
- Giải thích một span đáng chú ý: span `run` (generation) liên kết câu trả lời với
  managed prompt. Metadata gồm `prompt_name`, `prompt_label`, `prompt_version`,
  `prompt_source`, `doc_count` và `query_preview`, nên truy ngược được request đã dùng
  prompt version nào và kiểm chứng rollback an toàn.
  **Hạn chế đã ghi nhận**: hiện `@observe` chỉ bọc `agent.run()` nên trace chỉ có một
  span; trace nói được "chậm 3s" nhưng chưa nói được "chậm ở bước nào" — cần tách span
  `retrieval` và `llm`.

## 4. Prompt versioning

- Prompt name: `day13-chat`
- Version/label baseline: version 1, labels `baseline` và `production`
- Version/label candidate: version 2, label `candidate`
- Trace ID của mỗi version:
  - baseline v1: `7e89ea3111f42b814ad5b735b07d2f5f`
  - candidate v2: `fc60baea1602e9759d9807b9bcd15a01`
  - production sau rollback về v1: `bd16ddb65d4569681c162a85717e1023`
- Ảnh trace từng version: [`evidence/prompt_ver1.jpg`](evidence/prompt_ver1.jpg)
  (trace `7e89ea31…`, v1 label `baseline`) và
  [`evidence/prompt_ver2.jpg`](evidence/prompt_ver2.jpg)
  (trace `fc60baea…`, v2 label `candidate`) — cả hai đều `prompt_source=langfuse`
- Ảnh danh sách prompt: [`evidence/prompt_rollback.jpg`](evidence/prompt_rollback.jpg)
  — `day13-chat` có 2 version
- Bằng chứng đổi label hoặc rollback: [`evidence/checkpoint-2-tracing-prompt-versioning.md`](evidence/checkpoint-2-tracing-prompt-versioning.md)
  (label switch `production` → v2 rồi rollback về v1, kèm trace
  `bd16ddb65d4569681c162a85717e1023` chạy sau rollback)

## 5. Dashboard, SLO và alerts

- Kết quả `validate_dashboard.py`: `HỢP LỆ: 6/6 panel` từ baseline (xem
  [cp0_baseline_validate_logs.txt](evidence/cp0_baseline_validate_logs.txt));
  _(R3 chụp lại kèm ảnh dashboard runtime)_
- Evidence dashboard: _(R3)_
- SLO đã chọn và lý do: _(R3)_
- Alert rules và runbook: _(R3)_

## 6. Điều tra challenge

> Bằng chứng đầy đủ: [evidence/challenge/NOTES.md](evidence/challenge/NOTES.md).
> Diễn tập trước đó: [evidence/practice_rag_slow/NOTES.md](evidence/practice_rag_slow/NOTES.md).

- Challenge ID: `day13-k3-observability-v1` (incident `rag_slow`, feature `refund`,
  `latency_threshold_ms` = 2000)
- Triệu chứng từ metrics: p95/p99 tăng **1071ms → 2651ms**, vượt threshold 2000ms;
  error rate = 0, cost và token không đổi → sự cố latency thuần. **p50 không nhúc nhích**
  (150ms → 150ms) vì chỉ 5/16 request thuộc feature `refund` — chỉ số tổng thể che mất
  sự cố của một feature.
  ([01_metrics_before.json](evidence/challenge/01_metrics_before.json) ↔
  [04_metrics_during.json](evidence/challenge/04_metrics_during.json))
- Trace ID liên quan: **`91c8f0a41ee71bc7b766fed41c86933a`** (session `k3-challenge-s03`,
  latency 2.656s) — chi tiết trong
  [09_trace_detail_slowest.json](evidence/challenge/09_trace_detail_slowest.json).
  Cả 5 trace challenge ở 2.652–2.656s so với traffic nền 0.150–0.160s, và đều có
  `prompt_source=langfuse`, `prompt_version=1`, `prompt_label=production` → **loại trừ
  được prompt là nguyên nhân**
  ([08_langfuse_traces_list.txt](evidence/challenge/08_langfuse_traces_list.txt)).
  **Ghi nhận hạn chế**: trace chỉ có một observation (`GENERATION | run`) nên chỉ ra
  được "chậm 2.65s" nhưng chưa chỉ ra được "chậm ở bước nào".
- Log line/correlation ID liên quan: `req-ac1bd367`
  ([05_logs_by_correlation_id.jsonl](evidence/challenge/05_logs_by_correlation_id.jsonl));
  toàn bộ 5 request `refund` trong
  [06_all_refund_response_logs.jsonl](evidence/challenge/06_all_refund_response_logs.jsonl).
  Bảng nối `correlation_id` ↔ `session_id` ↔ `trace_id` trong
  [NOTES.md](evidence/challenge/NOTES.md).
- Root cause: bước retrieval của RAG chậm thêm ~2.5s mỗi request
  (`app/mock_rag.py:18` — `time.sleep(2.5)` khi flag `rag_slow` bật), tự nó đã vượt SLO.
  **Nghiêm trọng hơn**: lệnh sleep đồng bộ này nằm trong endpoint `async def`
  (`app/main.py:46`) nên khoá event loop, khiến các request đồng thời bị xếp hàng.
  [10_trace_timeline_serialization.txt](evidence/challenge/10_trace_timeline_serialization.txt)
  cho thấy 5 trace gửi đồng thời nhưng **mỗi trace bắt đầu đúng lúc trace trước kết
  thúc** — client đo tới **13281ms** trong khi server chỉ ghi `latency_ms ≈ 2650`.
  Metrics đang under-report latency thật vì chỉ đo `agent.run()`, không tính thời gian
  chờ hàng đợi.
- Fix action: (1) timeout ~500ms cho retrieval kèm fallback trả lời không có context;
  (2) đưa lời gọi chặn ra khỏi event loop (`run_in_threadpool` hoặc để `/chat` là `def`
  thường); (3) đo `latency_ms` từ middleware để phản ánh đúng trải nghiệm người dùng;
  (4) tách span `retrieval`/`llm` trong trace.
- Preventive measure: alert p95 **tách theo `feature`** (p50 tổng che mất sự cố của
  `refund`); alert trên chênh lệch client-latency vs server-`latency_ms` như dấu hiệu
  sớm của xếp hàng; quy ước review code cấm gọi hàm chặn trong endpoint `async`; load
  test định kỳ với `--concurrency > 1` vì chạy tuần tự không bao giờ lộ lỗi này.

## 7. Đóng góp cá nhân

Với mỗi thành viên, ghi rõ nhiệm vụ và link commit/PR tương ứng.

| Thành viên | Phần việc | Commit/PR | Điều đã học |
|---|---|---|---|
| Nguyễn Chí Hướng — 2A202601203 | Correlation ID middleware; JSON log enrichment; hash user ID; PII redaction; tests và evidence Checkpoint 1 | `5d55476` | Correlation ID cần được validate/propagate xuyên suốt request; PII phải được scrub ở processor cuối trước khi render JSON. |
| Phạm Thị Liên — 2A202601795 | Tracing; Langfuse prompt `day13-chat`; prompt v1/v2; label switch và rollback; trace metadata evidence Checkpoint 2 | `6b7d385` (PR #1) | Trace metadata phải gắn prompt name, label và version để truy ngược request đã dùng prompt nào. |
| Nguyễn Tiến Đạt — 2A202601387 | Role 3 — dashboard 6 panel, SLO, alert, runbook | | |
| Lê Quang Huy — 2A202601821 | Setup baseline; practice incident; chạy challenge chính thức; nối Metrics → Traces → Logs; report và kịch bản demo | `0cf830e`, `1ed3698`, `7b5e615` | Metrics chỉ nói "có sự cố", trace nói "chậm ở đâu", log mới chứng minh được nguyên nhân. Và chính metrics cũng có thể sai: `latency_ms` bỏ sót thời gian chờ hàng đợi nên báo 3.1s trong khi người dùng chịu 15.3s. |
