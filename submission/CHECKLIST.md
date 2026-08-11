# Checklist nộp bài — trạng thái hiện tại

> R4 rà theo [docs/grading-evidence.md](../docs/grading-evidence.md) và
> [SUBMISSION.md](../SUBMISSION.md). Cập nhật lần cuối: 2026-08-11.

## Evidence bắt buộc

| # | Yêu cầu | Trạng thái | Ở đâu |
|:-:|---|:-:|---|
| 1 | Kết quả cuối `validate_logs.py` | ✅ | [checkpoint-1-validate-logs.txt](evidence/checkpoint-1-validate-logs.txt) — 100/100 |
| 2 | Danh sách ≥10 traces | ✅ | 60 traces trên project chung; [08_langfuse_traces_list.txt](evidence/challenge/08_langfuse_traces_list.txt) |
| 3 | Một trace waterfall đầy đủ | ✅ | [prompt_ver1.jpg](evidence/prompt_ver1.jpg), [prompt_ver2.jpg](evidence/prompt_ver2.jpg) — cây span kèm metadata |
| 4 | Hai prompt version + trace đúng name/label/version | ✅ | [prompt_baseline.jpg](evidence/prompt_baseline.jpg) + [prompt_candidate.jpg](evidence/prompt_candidate.jpg) (v1/v2 và label), [prompt_ver1.jpg](evidence/prompt_ver1.jpg) + [prompt_ver2.jpg](evidence/prompt_ver2.jpg) (trace tương ứng) |
| 5 | Bằng chứng đổi label / rollback | ⚠️ | Cả 4 ảnh hiện có đều chụp **cùng một trạng thái**: `production` nằm ở v1 (tức là sau rollback). Thiếu ảnh lúc `production` đang ở v2 để thành cặp trước/sau. Thao tác đổi label mới chỉ được mô tả bằng text + trace ID trong [checkpoint-2-tracing-prompt-versioning.md](evidence/checkpoint-2-tracing-prompt-versioning.md) |
| 6 | Log JSON có correlation ID và metadata | ✅ | [checkpoint-1-logging-pii.md](evidence/checkpoint-1-logging-pii.md), [05_logs_by_correlation_id.jsonl](evidence/challenge/05_logs_by_correlation_id.jsonl) |
| 7 | Log chứng minh PII đã redact | ✅ | [checkpoint-1-logging-pii.md](evidence/checkpoint-1-logging-pii.md) |
| 8 | Kết quả `validate_dashboard.py` hợp lệ | ✅ | [cp0_baseline_validate_logs.txt](evidence/cp0_baseline_validate_logs.txt) — 6/6 panel |
| 9 | Dashboard đủ 6 nhóm chỉ số | ✅ | [dashboard_runtime_incident.png](evidence/dashboard_runtime_incident.png) — đủ 6 panel, chụp trong sự cố (p95 2651ms); kèm ảnh trạng thái bình thường [dashboard_runtime.png](evidence/dashboard_runtime.png) |
| 10 | Alert rules và runbook | ✅ | [config/alert_rules.yaml](../config/alert_rules.yaml) (3 alert) + [docs/alerts.md](../docs/alerts.md) (runbook đầy đủ) + [config/slo.yaml](../config/slo.yaml) |
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

1. **R2 (Liên)** — hạng mục 5, việc duy nhất còn thiếu: chụp màn hình version list của
   prompt `day13-chat` **lúc nhãn `production` đang nằm trên v2**. Ghép với
   `prompt_baseline.jpg` (production ở v1) là thành cặp trước/sau đúng yêu cầu đề.
   Cách làm: trên Langfuse mở prompt `day13-chat` → gán label `production` cho v2 →
   chụp → rollback `production` về v1 (trạng thái hiện tại, cần giữ nguyên vì trace
   challenge đã chạy với v1).
2. **Điền commit SHA cuối** vào mục 1 của REPORT.md ngay trước khi nộp:
   `git rev-parse HEAD`.
3. `app/pii.py:11` còn một `TODO` không bắt buộc (thêm pattern passport/địa chỉ) —
   `validate_logs.py` đã 100/100 nên không chặn nộp bài.
