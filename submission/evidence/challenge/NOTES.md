# Checkpoint 3 — Điều tra challenge chính thức

- Challenge ID: `day13-k3-observability-v1` (cohort K3)
- Incident: `rag_slow` · feature bị ảnh hưởng: `refund` · `latency_threshold_ms`: 2000
- Chạy ngày 2026-08-11 trên `main` đã có Checkpoint 1 của R1 (commit `5d55476`,
  `validate_logs.py` = 100/100 nên log có correlation ID và metadata đầy đủ).
- Langfuse chưa có key ở lần chạy này (`tracing_enabled: false`) → phần trace waterfall
  còn thiếu, R2 bổ sung sau. Hai tầng Metrics và Logs đã đủ bằng chứng.

## Các lệnh đã chạy

```bash
curl -s http://127.0.0.1:8000/metrics                      # 01_metrics_before.json
python scripts/inject_incident.py                          # 02_inject_incident.txt
python scripts/load_test.py --challenge --concurrency 5    # 03_load_test_challenge.txt
curl -s http://127.0.0.1:8000/metrics                      # 04_metrics_during.json
grep "req-714561b0" data/logs.jsonl                        # 05_logs_by_correlation_id.jsonl
python scripts/inject_incident.py --disable                # 07_disable_incident.txt
```

## Bước 1 — Metrics: triệu chứng

| Chỉ số | Trước | Trong incident |
|---|---|---|
| latency_p50 | 150 ms | 150 ms |
| latency_p95 | 151 ms | **2651 ms** |
| latency_p99 | 151 ms | **2651 ms** |
| error_breakdown | {} | {} |
| avg_cost_usd | 0.0020 | 0.0020 |
| quality_avg | 0.88 | 0.8733 |

p95/p99 vượt threshold 2000ms của challenge, trong khi **error rate = 0 và cost/token
không đổi** → sự cố latency thuần, không phải lỗi hay cost spike. p50 vẫn 150ms vì chỉ
5/15 request thuộc feature `refund` — **latency tổng thể che mất sự cố của một feature**.

## Bước 2 — Phát hiện quan trọng: metrics under-report latency thật

Client (`03_load_test_challenge.txt`) đo **13301 ms** mỗi request, nhưng log server ghi
`latency_ms: 2650`. Chênh lệch ~5 lần này chính là thứ dashboard không nhìn thấy.

`06_all_refund_response_logs.jsonl` — 5 request gửi đồng thời lúc ~03:18:39, nhưng
response hoàn tất **cách nhau đúng ~2.65s**:

```
03:18:41.939  req-714561b0  2650 ms
03:18:44.594  req-f075364e  2651 ms
03:18:47.251  req-daf0e8b7  2651 ms
03:18:49.907  req-4d0a9f5b  2651 ms
03:18:52.565  req-57219255  2651 ms
```

Chúng chạy **tuần tự chứ không song song**. Đây là bằng chứng request bị xếp hàng.

## Bước 3 — Logs chứng minh root cause

`05_logs_by_correlation_id.jsonl` — cặp `request_received` → `response_sent` của
`req-714561b0`, đầy đủ `correlation_id`, `user_id_hash` (đã hash), `session_id`,
`feature`, `model`, `env`; token và cost bình thường; **không có PII nguyên văn**.

Đối chiếu code:

1. `app/mock_rag.py:18` — khi flag `rag_slow` bật, `retrieve()` gọi `time.sleep(2.5)`,
   mô phỏng vector store chậm. Giải thích 2650ms trong `latency_ms`.
2. `app/main.py:46` — `/chat` khai báo `async def`, nhưng `agent.run()` gọi thẳng
   `time.sleep()` **đồng bộ**. Lệnh sleep chặn event loop, nên request thứ 2 phải chờ
   request thứ 1 xong. Giải thích khoảng cách 2.65s giữa các response và con số 13.3s
   phía client.

## Root cause

Bước retrieval của RAG chậm thêm ~2.5s mỗi request (vector store degrade). Riêng nó
đã vượt SLO 2000ms. **Nhưng thiệt hại thật lớn hơn nhiều**: vì `time.sleep` là lệnh
chặn nằm trong endpoint `async`, nó khoá event loop và làm mọi request đồng thời bị
xếp hàng — 5 người dùng đồng thời thì người cuối chờ 13.3s.

Đo lường cũng có lỗ hổng: `latency_ms` chỉ tính thời gian `agent.run()`, **không tính
thời gian request nằm chờ trong hàng đợi**, nên metrics báo 2651ms trong khi người dùng
thật chịu 13301ms.

## Fix action

1. **Timeout + fallback cho retrieval**: đặt hạn ~500ms cho lời gọi retrieval; quá hạn
   thì trả lời không kèm context thay vì chờ, kèm log `retrieval_timeout`.
2. **Không chặn event loop**: chuyển lời gọi retrieval đồng bộ sang
   `await run_in_threadpool(...)` (hoặc khai báo `/chat` là `def` thường để FastAPI tự
   đẩy vào threadpool). Việc này gỡ phần khuếch đại 13.3s ngay cả khi retrieval còn chậm.
3. **Đo latency từ đầu request**: tính `latency_ms` trong middleware (từ lúc nhận request
   đến lúc trả response) thay vì chỉ bọc `agent.run()`, để metrics phản ánh đúng trải
   nghiệm người dùng.

## Preventive measure

1. **Alert p95 latency tách theo `feature`**, không chỉ toàn hệ thống — trong sự cố này
   p50 tổng vẫn 150ms trong khi `refund` đã hỏng hoàn toàn.
2. **Alert riêng cho từng span/bước** (retrieval, LLM) để trace không phải là nơi duy
   nhất phát hiện bước nào chậm.
3. **Alert trên chênh lệch client-latency vs server-`latency_ms`** — khoảng cách giãn ra
   là dấu hiệu sớm của tình trạng xếp hàng, xuất hiện trước khi có error.
4. **Kiểm tra khi review code**: không gọi hàm chặn (`time.sleep`, I/O đồng bộ) trong
   endpoint `async`.
5. Load test định kỳ với `--concurrency > 1`; chạy tuần tự sẽ không bao giờ lộ lỗi này.
