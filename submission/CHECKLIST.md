# Checklist nộp bài — trạng thái hiện tại

> R4 rà theo [docs/grading-evidence.md](../docs/grading-evidence.md) và
> [SUBMISSION.md](../SUBMISSION.md). Cập nhật lần cuối: 2026-08-11.

## Evidence bắt buộc

| # | Yêu cầu | Trạng thái | Ở đâu |
|:-:|---|:-:|---|
| 1 | Kết quả cuối `validate_logs.py` | ✅ | [checkpoint-1-validate-logs.txt](evidence/checkpoint-1-validate-logs.txt) — 100/100 |
| 2 | Danh sách ≥10 traces | ✅ | 60 traces trên project chung; [08_langfuse_traces_list.txt](evidence/challenge/08_langfuse_traces_list.txt) |
| 3 | Một trace waterfall đầy đủ | ⚠️ | Có dữ liệu ([09_trace_detail_slowest.json](evidence/challenge/09_trace_detail_slowest.json)) nhưng **thiếu ảnh chụp UI** |
| 4 | Hai prompt version + trace đúng name/label/version | ✅ | [checkpoint-2-tracing-prompt-versioning.md](evidence/checkpoint-2-tracing-prompt-versioning.md) |
| 5 | Bằng chứng đổi label / rollback | ⚠️ | Đã ghi lại dạng text; **nên có thêm ảnh trước/sau** |
| 6 | Log JSON có correlation ID và metadata | ✅ | [checkpoint-1-logging-pii.md](evidence/checkpoint-1-logging-pii.md), [05_logs_by_correlation_id.jsonl](evidence/challenge/05_logs_by_correlation_id.jsonl) |
| 7 | Log chứng minh PII đã redact | ✅ | [checkpoint-1-logging-pii.md](evidence/checkpoint-1-logging-pii.md) |
| 8 | Kết quả `validate_dashboard.py` hợp lệ | ✅ | [cp0_baseline_validate_logs.txt](evidence/cp0_baseline_validate_logs.txt) — 6/6 panel |
| 9 | Dashboard đủ 6 nhóm chỉ số | ❌ | **R3 chưa làm** — cần ảnh dashboard runtime có time range, đơn vị, threshold |
| 10 | Alert rules và runbook | ❌ | **R3 chưa làm** — `config/alert_rules.yaml` còn nguyên `TODO` |
| 11 | Evidence điều tra challenge | ✅ | [evidence/challenge/](evidence/challenge/) + [NOTES.md](evidence/challenge/NOTES.md) |

## Kiểm tra kỹ thuật

| Lệnh | Kết quả |
|---|---|
| `python -m pytest -q` | ✅ 27 passed |
| `python scripts/validate_logs.py` | ✅ 100/100 |
| `python scripts/validate_dashboard.py` | ✅ 6/6 panel |
| `git status --short` | ✅ sạch sau mỗi lần commit |

## Điều kiện "không được nộp"

| Mục | Trạng thái |
|---|---|
| `.env`, API key, secret | ✅ `.env` bị `.gitignore` chặn, `git ls-files` không có; quét `sk-lf-`/`pk-lf-` trong repo đã commit: sạch |
| `.venv/`, cache, dependency | ✅ đã gitignore |
| Log có PII chưa che | ✅ `data/logs.jsonl` gitignore; evidence đã quét không có email/số điện thoại nguyên văn |
| `config/challenge.json` bị sửa | ✅ `git diff cd84f4f HEAD -- config/challenge.json` rỗng — nguyên vẹn từ bản release |

## Còn lại phải làm

1. **R3 (Đạt)** — hạng mục 9 và 10, đang chặn bài nộp:
   - Dựng dashboard 6 panel từ `data/logs.jsonl` theo
     [docs/DASHBOARD_SETUP.md](../docs/DASHBOARD_SETUP.md), chụp ảnh có time range,
     đơn vị và threshold.
   - Điền `config/alert_rules.yaml` (đang còn 3 khối `TODO`) và viết runbook.
   - Điền mục 5 của [REPORT.md](REPORT.md).
   - Gợi ý từ kết quả challenge: alert nên tách **p95 theo từng `feature`**, vì sự cố
     vừa rồi p50 tổng vẫn 150ms trong khi `refund` đã hỏng hoàn toàn.
2. **Ảnh chụp UI Langfuse** cho hạng mục 3 và 5 — dữ liệu đã có, chỉ thiếu screenshot.
3. **Điền commit SHA cuối** vào mục 1 của REPORT.md ngay trước khi nộp:
   `git rev-parse HEAD`.
4. `app/pii.py:11` còn một `TODO` không bắt buộc (thêm pattern passport/địa chỉ) —
   `validate_logs.py` đã 100/100 nên không chặn nộp bài.
