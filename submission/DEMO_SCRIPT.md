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

Mở dashboard, chỉ vào panel latency: p95 vượt threshold `2000ms` của challenge,
trong khi error rate phẳng và cost/token không đổi.

> Câu chốt: "Không phải lỗi, không phải cost — đây là sự cố latency, và nó chỉ
> đánh vào feature `refund`."

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

- **Root cause:** bước retrieval của RAG bị chậm, cộng thêm ~2.5s mỗi request
  (mô phỏng vector store timeout/degrade).
- **Fix:** đặt timeout cho lời gọi retrieval và fallback sang câu trả lời không có
  context thay vì chờ vô hạn.
- **Preventive:** alert trên p95 latency theo từng feature (không chỉ toàn hệ thống),
  vì tổng p50 vẫn đẹp trong khi `refund` đã hỏng; kèm runbook trỏ thẳng vào bước
  Metrics → Traces → Logs này.

## Phân vai khi demo

| Bước | Người nói |
|---|---|
| Metrics + dashboard | Nguyễn Tiến Đạt (R3) |
| Traces + prompt version | Phạm Thị Liên (R2) |
| Logs + PII | Nguyễn Chí Hướng (R1) |
| Root cause / fix / preventive + chốt | Lê Quang Huy (R4) |
