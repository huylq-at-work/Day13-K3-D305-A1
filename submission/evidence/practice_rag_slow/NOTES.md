# Practice run — scenario `rag_slow` (diễn tập cho Checkpoint 3)

> Đây là **practice**, không phải challenge chính thức. Mục đích: R4 diễn tập trước
> quy trình Metrics → Traces → Logs → Root cause để khi chạy challenge thật
> (`config/challenge.json`, cùng scenario `rag_slow`) không mất thời gian mò.
> Chạy lúc code còn ở baseline (R1–R3 chưa merge), ngày 2026-08-11, commit `0cf830e`.

## Các bước đã chạy

```bash
# 1. Chụp metrics trước incident
curl -s http://127.0.0.1:8000/metrics   # -> metrics_before.json

# 2. Bật incident practice
python scripts/inject_incident.py --scenario rag_slow

# 3. Tạo traffic
python scripts/load_test.py             # -> load_test_during_incident.txt

# 4. Chụp metrics trong incident
curl -s http://127.0.0.1:8000/metrics   # -> metrics_during.json

# 5. Tắt incident
python scripts/inject_incident.py --scenario rag_slow --disable
```

## Kết quả — luồng điều tra

**Bước 1 — Metrics phát hiện sự cố:**

| Chỉ số | Trước | Trong incident |
|---|---|---|
| latency_p50 | 150 ms | 151 ms |
| latency_p95 | 151 ms | **2651 ms** |
| latency_p99 | 151 ms | **2651 ms** |
| error_breakdown | {} | {} (không có error) |
| avg_cost_usd | 0.0022 | 0.0021 (không đổi) |

Triệu chứng: **p95/p99 tăng ~17 lần, không có error, cost và token không đổi** →
đây là sự cố latency thuần, không phải lỗi hay cost spike.

**Bước 2 — Trace khoanh vùng:** chưa làm được ở bản baseline (tracing_enabled=false,
chờ R2 + Langfuse key). Khi chạy challenge thật, mở trace waterfall để chỉ ra span
retrieval chiếm ~2.5s trong tổng ~2.66s.

**Bước 3 — Log chứng minh:** `slow_log_lines.jsonl` cho thấy các record
`response_sent` có `latency_ms: 2651` đồng loạt sau thời điểm bật incident,
`quality_score` và token bình thường. (Bản baseline chưa có `correlation_id` —
chờ R1 để dẫn chứng theo từng request.)

**Root cause (đối chiếu code):** khi flag `rag_slow` bật, `app/mock_rag.py:18`
chèn `time.sleep(2.5)` vào `retrieve()` — mô phỏng vector store/retrieval bị chậm.
Toàn bộ độ trễ tăng thêm (~2500ms) nằm ở bước retrieval, khớp với chênh lệch
metrics (151ms → 2651ms).

## Checklist khi chạy challenge chính thức (sau khi R1–R3 merge)

1. `git pull` main đã đủ phần R1 (correlation ID), R2 (tracing), R3 (dashboard/SLO).
2. Restart API, chụp `/metrics` trước.
3. `python scripts/inject_incident.py` (không tham số — đọc `config/challenge.json`).
4. `python scripts/load_test.py --challenge --concurrency 5`.
5. Chụp `/metrics` sau; đối chiếu `latency_threshold_ms: 2000` của challenge.
6. Lấy trace ID của request feature `refund` chậm, chụp waterfall.
7. Lọc log theo `correlation_id` của trace đó, lưu log line làm bằng chứng.
8. Tắt incident, ghi root cause + fix + preventive vào REPORT.md mục 6.
