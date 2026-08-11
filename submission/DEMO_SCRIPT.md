# Kịch bản demo cuối buổi (Role 4)

> Luồng bắt buộc theo [CHECKPOINTS.md](../CHECKPOINTS.md): **Metrics → Traces → Logs → Root cause**.
> Mục tiêu: ~5 phút, mỗi bước phải chỉ được **bằng chứng cụ thể trên màn hình**, không nói chay.

## Chuẩn bị trước khi demo

```bash
git pull origin main
python -m pytest -q
python scripts/validate_logs.py
python scripts/validate_dashboard.py
```

API chạy sẵn ở terminal riêng, dashboard và Langfuse mở sẵn tab.

## Bước 1 — Metrics: "có chuyện gì đó"

Mở dashboard ([`evidence/dashboard_runtime_incident.png`](evidence/dashboard_runtime_incident.png)),
chỉ vào panel Latency: p95/p99 = **2651ms** trong khi p50 vẫn **150ms**, error rate
0.00%, cost và token không đổi.

> Câu chốt 1: "Không phải lỗi, không phải cost — đây là sự cố latency, và nó chỉ
> đánh vào feature `refund`. p50 tổng vẫn đẹp vì chỉ 5/16 request là refund."

Rồi chỉ vào **badge xanh "Thresh: 3000"** ngay dưới con số 2651.

> Câu chốt 2: "Và đây là lý do nhóm hạ SLO xuống 2000ms — với ngưỡng mặc định, dashboard
> vẫn báo xanh ngay giữa lúc sự cố đang diễn ra."

## Bước 2 — Traces: "chậm ở đâu"

Mở Langfuse, lọc trace theo feature `refund`, chọn một trace chậm. Mở waterfall,
chỉ vào span retrieval chiếm phần lớn tổng thời gian.

> Câu chốt: "Span retrieval ăn ~2.5s trong tổng ~2.6s. LLM span vẫn bình thường."

Nói thêm trace đó gắn `prompt_name` / `prompt_label` / `prompt_version` nào — chứng
minh prompt không phải biến số gây ra sự cố.

## Bước 3 — Logs: "chứng minh"

Lấy `correlation_id` từ trace, lọc trong `data/logs.jsonl`:

```bash
grep "<correlation_id>" data/logs.jsonl
```

Chỉ ra cặp `request_received` → `response_sent` cùng một correlation ID, với
`latency_ms` cao và token/cost bình thường. Đồng thời chỉ ra log **không có PII
nguyên văn** (email/số điện thoại đã bị che).

## Bước 4 — Root cause, fix, preventive

Điểm nhấn của nhóm: **không dừng ở "retrieval chậm"**.

- **Root cause tầng 1:** retrieval của RAG chậm thêm ~2.5s/request → tự nó đã vượt
  SLO 2000ms.
- **Root cause tầng 2 (phần đáng nói):** lệnh chặn đó nằm trong endpoint `async`, khoá
  event loop. Chiếu `10_trace_timeline_serialization.txt` lên màn hình — 5 trace gửi
  đồng thời nhưng **mỗi trace bắt đầu đúng lúc trace trước kết thúc**. Client chịu
  **13.3s** trong khi server chỉ ghi `latency_ms: 2650`.

> Câu chốt: "Dashboard báo 2.6s, người dùng thật chờ 13.3s. Metrics của chúng tôi
> đang đo sai chỗ — nó không tính thời gian nằm chờ trong hàng đợi."

- **Fix:** timeout + fallback cho retrieval; đưa lời gọi chặn ra khỏi event loop; đo
  latency từ middleware thay vì chỉ bọc `agent.run()`.
- **Preventive:** alert p95 tách theo từng feature (p50 tổng vẫn 150ms trong khi
  `refund` đã hỏng hoàn toàn); alert trên chênh lệch client vs server latency; load test
  luôn chạy `--concurrency > 1`.

Chi tiết và số liệu: [evidence/challenge/NOTES.md](evidence/challenge/NOTES.md).

## Phân vai khi demo

| Bước | Người nói |
|---|---|
| Metrics + dashboard | Nguyễn Tiến Đạt (R3) |
| Traces + prompt version | Phạm Thị Liên (R2) |
| Logs + PII | Nguyễn Chí Hướng (R1) |
| Root cause / fix / preventive + chốt | Lê Quang Huy (R4) |
