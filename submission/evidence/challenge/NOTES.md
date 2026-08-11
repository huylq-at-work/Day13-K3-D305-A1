# Checkpoint 3 — Điều tra challenge chính thức

- Challenge ID: `day13-k3-observability-v1` (cohort K3)
- Incident: `rag_slow` · feature bị ảnh hưởng: `refund` · `latency_threshold_ms`: 2000
- Chạy ngày 2026-08-11 trên `main` đã có Checkpoint 1 của R1 (`5d55476`) và
  Checkpoint 2 của R2 (`6b7d385`).
- Chạy trên **project Langfuse chung của nhóm**, dùng managed prompt `day13-chat`
  version 1 label `production` do R2 tạo — trace ghi `prompt_source=langfuse`, không
  còn `local-fallback`. Đủ ba tầng Metrics → Traces → Logs.

## Các lệnh đã chạy

```bash
python scripts/load_test.py                                # traffic nền
curl -s http://127.0.0.1:8000/metrics                      # 01_metrics_before.json
python scripts/inject_incident.py                          # 02_inject_incident.txt
python scripts/load_test.py --challenge --concurrency 5    # 03_load_test_challenge.txt
curl -s http://127.0.0.1:8000/metrics                      # 04_metrics_during.json
python scripts/inject_incident.py --disable                # 07_disable_incident.txt
# GET {LANGFUSE_HOST}/api/public/traces                    # 08, 09, 10
```

## Bước 1 — Metrics: triệu chứng

| Chỉ số | Trước | Trong incident |
|---|---|---|
| latency_p50 | 150 ms | 150 ms |
| latency_p95 | 1071 ms | **2651 ms** |
| latency_p99 | 1071 ms | **2651 ms** |
| error_breakdown | {} | {} |
| avg_cost_usd | 0.0021 | 0.0021 |
| quality_avg | 0.8818 | 0.875 |

p95/p99 vượt threshold **2000 ms**, trong khi **error rate = 0, cost và token không
đổi** → sự cố latency thuần, không phải lỗi hay cost spike.

Hai chi tiết dễ bị bỏ qua:

- **p50 không nhúc nhích** (150ms → 150ms) vì chỉ 5/16 request thuộc feature `refund`.
  Chỉ số tổng thể che mất sự cố của một feature.
- p95 "trước" là 1071ms không phải vì hệ thống chậm, mà vì request đầu tiên phải fetch
  prompt từ Langfuse (chưa cache). Đây là nhiễu cần biết để không chẩn đoán nhầm.

## Bước 2 — Traces: khoanh vùng

`08_langfuse_traces_list.txt` — hai nhóm tách bạch hoàn toàn:

| Nhóm | Session | Latency |
|---|---|---|
| Challenge (`refund`) | `k3-challenge-s01`…`s05` | 2.652 – 2.656 s |
| Traffic nền (`qa`/`summary`) | `s01`…`s10` | 0.150 – 0.160 s |

Cả 5 trace challenge đều có `prompt_source=langfuse`, `prompt_version=1`,
`prompt_label=production` → **prompt không phải biến số gây ra sự cố**, loại trừ được
ngay một giả thuyết.

Trace mẫu: **`91c8f0a41ee71bc7b766fed41c86933a`** (session `k3-challenge-s03`,
latency 2.656s) — chi tiết trong `09_trace_detail_slowest.json`.

> **Hạn chế phát hiện được ở tầng trace:** trace chỉ có **một observation**
> (`GENERATION | run`), tức toàn bộ `agent.run()` gói trong một span. Trace nói được
> "chậm 2.65s" nhưng **không nói được "chậm ở bước nào"** — phải mở code mới biết là
> retrieval. Cần tách span `retrieval` và `llm`.

## Bước 3 — Bằng chứng request bị xếp hàng

Client (`03_load_test_challenge.txt`) đo latency tăng dần theo bậc thang, trong khi
server chỉ ghi `latency_ms ≈ 2650`:

```
req-ac1bd367   7971 ms
req-46f83bc9  10628 ms
req-69315f64  13281 ms
req-19a92afe  13281 ms
req-404ed61b  13281 ms
```

`10_trace_timeline_serialization.txt` — cửa sổ thời gian của 5 trace cho thấy **mỗi
trace bắt đầu gần đúng lúc trace trước kết thúc**:

```
04:12:35.825 → 04:12:38.477   s04
04:12:38.480 → 04:12:41.133   s01
04:12:41.133 → 04:12:43.787   s02
04:12:43.787 → 04:12:46.441   s05
04:12:46.441 → 04:12:49.097   s03
```

5 request gửi đồng thời nhưng **chạy tuần tự chứ không song song**. `13281 ms ≈ 5 ×
2.65 s`.

## Bước 4 — Logs: chứng minh và nối các tầng

`05_logs_by_correlation_id.jsonl` — cặp `request_received` → `response_sent` của
`req-ac1bd367`, đủ `correlation_id`, `user_id_hash` (đã hash), `session_id`, `feature`,
`model`, `env`; token và cost bình thường; **không có PII nguyên văn**.

Nối trọn ba tầng qua `session_id`:

| correlation_id | session_id | trace_id | latency_ms (log) | latency (trace) |
|---|---|---|---|---|
| `req-46f83bc9` | `k3-challenge-s01` | `8615396b7dcefc9f944ee2b9fa802259` | 2651 | 2.653 s |
| `req-69315f64` | `k3-challenge-s02` | `0d61d1ff8a11a07a8e2862d529a3550e` | 2651 | 2.654 s |
| `req-404ed61b` | `k3-challenge-s03` | `91c8f0a41ee71bc7b766fed41c86933a` | 2650 | 2.656 s |
| `req-ac1bd367` | `k3-challenge-s04` | `b723bbfd0ee63c07dbd8f13cffe78e35` | 2650 | 2.652 s |
| `req-19a92afe` | `k3-challenge-s05` | `ccff69ab9017cab83395887ee82b9dff` | 2650 | 2.654 s |

## Root cause

Đối chiếu code:

1. `app/mock_rag.py:18` — khi flag `rag_slow` bật, `retrieve()` gọi `time.sleep(2.5)`,
   mô phỏng vector store degrade. Giải thích ~2.5s trong tổng 2.65s.
2. `app/main.py:46` — `/chat` khai báo `async def`, nhưng `agent.run()` gọi thẳng
   `time.sleep()` **đồng bộ**. Lệnh này chặn event loop, nên request thứ hai phải chờ
   request thứ nhất xong hẳn.

Retrieval chậm ~2.5s/request tự nó đã vượt SLO 2000ms. **Nhưng thiệt hại thật lớn hơn
nhiều** vì lệnh chặn nằm trong endpoint `async` — 5 người dùng đồng thời thì người cuối
chờ 13.3s.

Đo lường cũng có lỗ hổng: `latency_ms` chỉ tính thời gian `agent.run()`, **không tính
thời gian request nằm chờ trong hàng đợi**, nên metrics báo 2.65s trong khi người dùng
thật chịu 13.3s.

`11_server_logs_blind_to_queueing.txt` cho thấy vấn đề còn sâu hơn: **không chỉ
`latency_ms` sai, mà cả bản thân log cũng không chứa thông tin để sửa lại.** Khoảng cách
wall-clock giữa `request_received` và `response_sent` là 2652–2656ms — khớp gần như
tuyệt đối với `latency_ms`, không hề lộ ra 13.3s. Lý do: `request_received` chỉ được ghi
khi handler async cuối cùng giành được event loop, nên **thời gian xếp hàng nằm ngoài
vòng đời mà log quan sát được**. Chỉ một phép đo từ bên ngoài (synthetic probe) mới thấy
được.

## Fix action

1. **Timeout + fallback cho retrieval**: hạn ~500ms cho lời gọi retrieval; quá hạn thì
   trả lời không kèm context thay vì chờ, kèm log `retrieval_timeout`.
2. **Không chặn event loop**: đưa lời gọi đồng bộ sang `await run_in_threadpool(...)`,
   hoặc khai báo `/chat` là `def` thường để FastAPI tự đẩy vào threadpool. Việc này gỡ
   phần khuếch đại 13.3s ngay cả khi retrieval vẫn chậm.
3. **Đo latency từ đầu request**: tính `latency_ms` trong middleware (từ lúc nhận
   request đến lúc trả response) thay vì chỉ bọc `agent.run()`.
4. **Tách span trong trace**: thêm span riêng cho `retrieval` và `llm` để trace tự chỉ
   ra bước nào chậm, không phải mở code.

## Preventive measure

1. **Alert p95 latency tách theo `feature`**, không chỉ toàn hệ thống — ở sự cố này p50
   tổng vẫn 150ms trong khi `refund` đã hỏng hoàn toàn.
2. **Alert trên chênh lệch client-latency vs server-`latency_ms`** — khoảng cách giãn ra
   là dấu hiệu sớm của xếp hàng, xuất hiện trước khi có error.
3. **Kiểm tra khi review code**: cấm gọi hàm chặn (`time.sleep`, I/O đồng bộ) trong
   endpoint `async`.
4. **Load test định kỳ với `--concurrency > 1`** — chạy tuần tự sẽ không bao giờ lộ lỗi
   này, vì mỗi request lẻ vẫn chỉ 2.65s.
