# Checkpoint 3 — Điều tra challenge chính thức

- Challenge ID: `day13-k3-observability-v1` (cohort K3)
- Incident: `rag_slow` · feature bị ảnh hưởng: `refund` · `latency_threshold_ms`: 2000
- Chạy ngày 2026-08-11 trên `main` đã có Checkpoint 1 của R1 (commit `5d55476`,
  `validate_logs.py` = 100/100).
- **Langfuse Cloud region JP đã bật** (`tracing_enabled: true`), nên lần chạy này có đủ
  cả ba tầng Metrics → Traces → Logs.

## Các lệnh đã chạy

```bash
python scripts/load_test.py                                # traffic nền
curl -s http://127.0.0.1:8000/metrics                      # 01_metrics_before.json
python scripts/inject_incident.py                          # 02_inject_incident.txt
python scripts/load_test.py --challenge --concurrency 5    # 03_load_test_challenge.txt
curl -s http://127.0.0.1:8000/metrics                      # 04_metrics_during.json
python scripts/inject_incident.py --disable                # 07_disable_incident.txt
# GET {LANGFUSE_HOST}/api/public/traces                    # 08, 09
```

## Bước 1 — Metrics: triệu chứng

| Chỉ số | Trước | Trong incident |
|---|---|---|
| latency_p50 | 559 ms | 567 ms |
| latency_p95 | 593 ms | **3107 ms** |
| latency_p99 | 593 ms | **3107 ms** |
| error_breakdown | {} | {} |
| avg_cost_usd | 0.0022 | 0.0021 |
| quality_avg | 0.8818 | 0.875 |

p95/p99 vượt threshold 2000ms, trong khi **error rate = 0 và cost/token không đổi** →
sự cố latency thuần. p50 gần như không đổi vì chỉ 5/16 request thuộc feature `refund`:
**chỉ số tổng thể che mất sự cố của một feature**.

## Bước 2 — Traces: khoanh vùng

`08_langfuse_traces_list.txt` — 16 traces, tách bạch rõ hai nhóm:

| Nhóm | Session | Latency |
|---|---|---|
| Challenge (`refund`) | `k3-challenge-s01`…`s05` | 3.024 – 3.111 s |
| Traffic nền (`qa`/`summary`) | `s01`…`s10` | 0.542 – 0.597 s |

Trace chậm nhất lấy làm mẫu: **`a84f1d6e49d2d64472358dbc185fdfc0`**
(session `k3-challenge-s05`, latency 3.095s) — chi tiết trong
`09_trace_detail_slowest.json`, metadata có đủ `prompt_name`, `prompt_label`,
`prompt_version`, `prompt_source`.

> **Hạn chế phát hiện được ở tầng trace:** trace chỉ có **một observation duy nhất**
> (`GENERATION | run`, 3.095s), tức là toàn bộ `agent.run()` gói trong một span. Không
> có span riêng cho retrieval và LLM, nên **trace nói được "chậm 3s" nhưng không nói
> được "chậm ở bước nào"**. Đây là điểm cần R2 bổ sung: tách span `retrieval` và span
> `llm` bằng `@observe` để lần sau không phải mở code mới biết.

## Bước 3 — Logs: chứng minh

`05_logs_by_correlation_id.jsonl` — cặp `request_received` → `response_sent` của
`req-a256e453`, đủ `correlation_id`, `user_id_hash` (đã hash), `session_id`, `feature`,
`model`, `env`; token và cost bình thường; **không có PII nguyên văn**.

Nối trace ↔ log qua `session_id`:

| correlation_id | session_id | trace_id | latency_ms (log) |
|---|---|---|---|
| `req-e7c46e89` | `k3-challenge-s01` | `153637112f32ff41e625692a66087d89` | 3053 |
| `req-3e1a978d` | `k3-challenge-s02` | `173e4f72399f4fe2e869d004b5ee4938` | 3023 |
| `req-5fa776c6` | `k3-challenge-s03` | `ca9e3182e968700466dbb58f8c2f03e3` | 3043 |
| `req-4b9c08bd` | `k3-challenge-s04` | `530c6f1f83940f8b26782072982f7c33` | 3107 |
| `req-a256e453` | `k3-challenge-s05` | `a84f1d6e49d2d64472358dbc185fdfc0` | 3082 |

## Bước 4 — Phát hiện quan trọng: metrics under-report latency thật

Client (`03_load_test_challenge.txt`) đo **15339 ms** mỗi request, nhưng log server ghi
`latency_ms ≈ 3050` và trace ghi 3.09s. Chênh ~5 lần này là thứ dashboard không thấy.

`06_all_refund_response_logs.jsonl` — 5 request gửi đồng thời lúc ~03:57:39 nhưng
response hoàn tất **cách nhau đúng ~3.05s**:

```
03:57:42.398  req-a256e453  3082 ms
03:57:45.456  req-e7c46e89  3053 ms
03:57:48.485  req-3e1a978d  3023 ms
03:57:51.535  req-5fa776c6  3043 ms
03:57:54.646  req-4b9c08bd  3107 ms
```

Chúng chạy **tuần tự chứ không song song** — bằng chứng request bị xếp hàng.
`15339 ms ≈ 5 × 3.07 s`.

## Root cause

Đối chiếu code:

1. `app/mock_rag.py:18` — khi flag `rag_slow` bật, `retrieve()` gọi `time.sleep(2.5)`,
   mô phỏng vector store degrade. Giải thích ~2.5s trong tổng ~3.05s (phần còn lại là
   overhead LLM giả và Langfuse).
2. `app/main.py:46` — `/chat` khai báo `async def`, nhưng `agent.run()` gọi thẳng
   `time.sleep()` **đồng bộ**. Lệnh này chặn event loop, nên request thứ hai phải chờ
   request thứ nhất xong hẳn.

Vậy: retrieval chậm ~2.5s/request tự nó đã vượt SLO 2000ms. **Nhưng thiệt hại thật lớn
hơn nhiều** vì lệnh chặn nằm trong endpoint `async` — 5 người dùng đồng thời thì người
cuối chờ 15.3s.

Đo lường cũng có lỗ hổng: `latency_ms` chỉ tính thời gian `agent.run()`, **không tính
thời gian request nằm chờ trong hàng đợi**, nên metrics báo 3.1s trong khi người dùng
thật chịu 15.3s.

## Fix action

1. **Timeout + fallback cho retrieval**: hạn ~500ms cho lời gọi retrieval; quá hạn thì
   trả lời không kèm context thay vì chờ, kèm log `retrieval_timeout`.
2. **Không chặn event loop**: đưa lời gọi đồng bộ sang `await run_in_threadpool(...)`,
   hoặc khai báo `/chat` là `def` thường để FastAPI tự đẩy vào threadpool. Việc này gỡ
   phần khuếch đại 15.3s ngay cả khi retrieval vẫn chậm.
3. **Đo latency từ đầu request**: tính `latency_ms` trong middleware (từ lúc nhận
   request đến lúc trả response) thay vì chỉ bọc `agent.run()`.
4. **Tách span trong trace**: thêm span riêng cho `retrieval` và `llm` để trace tự chỉ
   ra bước nào chậm.

## Preventive measure

1. **Alert p95 latency tách theo `feature`**, không chỉ toàn hệ thống — ở sự cố này p50
   tổng vẫn 567ms trong khi `refund` đã hỏng hoàn toàn.
2. **Alert trên chênh lệch client-latency vs server-`latency_ms`** — khoảng cách giãn ra
   là dấu hiệu sớm của xếp hàng, xuất hiện trước khi có error.
3. **Kiểm tra khi review code**: cấm gọi hàm chặn (`time.sleep`, I/O đồng bộ) trong
   endpoint `async`.
4. **Load test định kỳ với `--concurrency > 1`** — chạy tuần tự sẽ không bao giờ lộ lỗi
   này, vì mỗi request lẻ vẫn chỉ 3s.
