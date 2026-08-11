# Checklist nộp bài — trạng thái hiện tại

> R4 rà theo [docs/grading-evidence.md](../docs/grading-evidence.md) và
> [SUBMISSION.md](../SUBMISSION.md). Cập nhật lần cuối: 2026-08-11.

## Evidence bắt buộc

| # | Yêu cầu | Trạng thái | Ở đâu |
|:-:|---|:-:|---|
| 1 | Kết quả cuối `validate_logs.py` | ✅ | [checkpoint-1-validate-logs.txt](evidence/checkpoint-1-validate-logs.txt) — 100/100 |
| 2 | Danh sách ≥10 traces | ✅ | 60 traces trên project chung; [08_langfuse_traces_list.txt](evidence/challenge/08_langfuse_traces_list.txt) |
| 3 | Một trace waterfall đầy đủ | ✅ | [prompt_ver1.jpg](evidence/prompt_ver1.jpg), [prompt_ver2.jpg](evidence/prompt_ver2.jpg) — cây span kèm metadata |
| 4 | Hai prompt version + trace đúng name/label/version | ✅ | Ảnh trên (v1 `baseline`, v2 `candidate`, `prompt_source=langfuse`) + [checkpoint-2-tracing-prompt-versioning.md](evidence/checkpoint-2-tracing-prompt-versioning.md) |
| 5 | Bằng chứng đổi label / rollback | ⚠️ | [prompt_rollback.jpg](evidence/prompt_rollback.jpg) mới chỉ chụp **danh sách prompt có 2 version**; text đã mô tả label switch + rollback. Đề yêu cầu **ảnh trước/sau khi đổi label `production`** — nên chụp bổ sung |
| 6 | Log JSON có correlation ID và metadata | ✅ | [checkpoint-1-logging-pii.md](evidence/checkpoint-1-logging-pii.md), [05_logs_by_correlation_id.jsonl](evidence/challenge/05_logs_by_correlation_id.jsonl) |
| 7 | Log chứng minh PII đã redact | ✅ | [checkpoint-1-logging-pii.md](evidence/checkpoint-1-logging-pii.md) |
| 8 | Kết quả `validate_dashboard.py` hợp lệ | ✅ | [cp0_baseline_validate_logs.txt](evidence/cp0_baseline_validate_logs.txt) — 6/6 panel |
| 9 | Dashboard đủ 6 nhóm chỉ số | ⚠️ | [dashboard_runtime.png](evidence/dashboard_runtime.png) + [scripts/dashboard.py](../scripts/dashboard.py). Ảnh chụp lúc log **chưa có incident** (p50=p95=p99=150ms, biểu đồ trống) và chỉ thấy 2/6 panel — **nên chụp lại sau khi chạy challenge** |
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

1. **R3 (Đạt)** — hạng mục 9: chụp lại ảnh dashboard **sau khi chạy challenge**, cuộn
   hết để thấy đủ 6 panel. Ảnh hiện tại chụp lúc log chưa có sự cố nên p50/p95/p99 đều
   bằng 150ms và biểu đồ latency trống — không thể hiện được gì.
   Cách làm: `python scripts/inject_incident.py` → `python scripts/load_test.py
   --challenge --concurrency 5` → mở dashboard rồi chụp → `python
   scripts/inject_incident.py --disable`.
2. **R2 (Liên)** — hạng mục 5: chụp thêm một ảnh **trước/sau khi đổi label
   `production`** (màn hình version list của prompt `day13-chat` lúc `production` đang
   ở v2, và lúc đã rollback về v1). Ảnh `prompt_rollback.jpg` hiện tại mới chỉ chứng
   minh có 2 version, chưa chứng minh thao tác đổi label.
3. **Điền commit SHA cuối** vào mục 1 của REPORT.md ngay trước khi nộp:
   `git rev-parse HEAD`.
4. `app/pii.py:11` còn một `TODO` không bắt buộc (thêm pattern passport/địa chỉ) —
   `validate_logs.py` đã 100/100 nên không chặn nộp bài.
