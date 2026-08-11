# DANH SÁCH THÀNH VIÊN NHÓM

> Day 13 Lab — Observability cho hệ thống AI · Đại học VinUni
> Repo: `Day13-K3-D305-A1`

## 1. Thành viên

| STT | Họ và tên | Mã sinh viên |
| :-: | :-- | :-- |
| 1 | Nguyễn Chí Hướng | 2A202601203 |
| 2 | Nguyễn Tiến Đạt | 2A202601387 |
| 3 | Phạm Thị Liên | 2A202601795 |
| 4 | Lê Quang Huy | 2A202601821 |

## 2. Phân công vai trò

Bốn vai trò lấy nguyên từ bảng "Phân vai nhóm" trong [README.md](README.md), chia theo
**file sở hữu** để không giẫm chân nhau khi cùng làm trên `main`.

| Thành viên | Vai trò | File sở hữu (chỉ người này được sửa) | Evidence phải bàn giao |
| :-- | :-- | :-- | :-- |
| Nguyễn Chí Hướng | Role 1 — Logging & PII | `app/middleware.py`, `app/logging_config.py`, `app/pii.py`, `app/main.py` | `validate_logs.py` ≥ 80/100, log có correlation ID, log đã che PII |
| Phạm Thị Liên | Role 2 — Tracing & Prompt Version | `app/tracing.py`, `app/prompt_management.py`, `app/agent.py` | ≥ 10 traces có metadata, hai trace ID gắn prompt v1/v2, ảnh đổi label/rollback |
| Nguyễn Tiến Đạt | Role 3 — Dashboard, SLO & Alert | `config/alert_rules.yaml`, `config/slo.yaml` | `validate_dashboard.py` báo `6/6 panel`, ảnh dashboard có time range/đơn vị/threshold, runbook |
| Lê Quang Huy | Role 4 — Incident, Report & Demo | `submission/REPORT.md`, `submission/evidence/` | root cause nối Metrics → Traces → Logs, fix, preventive measure, demo cuối |

Các khối `TODO` hiện có nằm gọn trong file sở hữu của R1 (`middleware.py`, `logging_config.py`,
`pii.py`, `main.py`) và R3 (`alert_rules.yaml`) — đúng người đúng file, không sửa hộ nhau.

### Quy tắc sở hữu file — đọc kỹ

**Không ai được sửa `config/challenge.json`** — file này do Lab Coach release, tự tạo hoặc
sửa là vi phạm [RULES.md](RULES.md). Tương tự, `config/dashboard.yaml` và
`config/logging_schema.json` là **contract để validator chấm**, không phải chỗ để sửa cho
pass: R3 dựng dashboard theo contract, không đổi contract theo dashboard.

`data/logs.jsonl` là file sinh ra khi chạy app — không ai commit tay nội dung vào đó, và
không commit log chứa PII chưa che.

R2 cần metadata trong log (`prompt_name`, `prompt_version`…) thì trao đổi để R1 thêm vào
phần enrich trong `main.py`, không tự sửa file của R1.

`submission/REPORT.md` do R4 giữ khung; mỗi người viết đúng mục thuộc vai mình và pull
về ngay trước khi viết. Evidence của ai người đó bỏ vào `submission/evidence/` với tên
file mô tả rõ nội dung.

## 3. Quy trình Git

Mỗi người **tự tách branch và mở Pull Request như bình thường** — nhóm không quy định
tên branch, không phân người review cố định. Ai xong phần mình thì mở PR vào `main`,
nhờ một thành viên bất kỳ xem qua rồi merge.

Vài điểm vẫn nên giữ để đỡ khổ nhau:

- PR body ghi rõ **làm gì và validator/test đạt bao nhiêu** — đó cũng là nguyên liệu
  cho REPORT.md.
- Commit đúng file thuộc vai mình, tránh `git add .` kéo nhầm file người khác hoặc
  file không được commit (mục 4).
- Pull `main` về branch của mình thường xuyên để không lệch xa.

### Thứ tự làm việc

Dashboard đọc từ `data/logs.jsonl`, và challenge chỉ có ý nghĩa khi log/trace đã chuẩn.
Nên thứ tự là:

1. **R1** xong correlation ID, JSON log, PII redaction trước — không có log chuẩn thì
   trace và dashboard đều thiếu dữ liệu.
2. **R2** hoàn thiện tracing + prompt v1/v2.
3. **R3** pull code mới, chạy `load_test.py` để sinh `data/logs.jsonl` rồi mới dựng
   dashboard, SLO, alert.
4. **R4** chỉ chạy challenge (`inject_incident.py` + `load_test.py --challenge`) khi
   `main` đã có đủ phần của ba người trên — nếu không, evidence trong report sẽ không
   khớp code.

### Xử lý conflict

Bảng sở hữu file ở mục 2 được thiết kế để **không có conflict**. Nếu vẫn xảy ra conflict,
nghĩa là ai đó đã sửa file không thuộc phần mình — dừng lại, hỏi trong nhóm, đừng tự
resolve. File hay bị đụng nhất là `submission/REPORT.md` vì cả nhóm cùng viết; quy ước:
mỗi người chỉ sửa đúng mục của mình, pull về ngay trước khi viết.

## 4. Không commit

`.env`, API key hoặc Langfuse key dưới mọi dạng, `.venv/`, `__pycache__/`, và log chứa
PII chưa che. Kiểm tra bằng `git status` trước mỗi lần commit.
