# Bằng chứng đổi label và rollback prompt `production`

> Bổ sung cho Checkpoint 2. Thực hiện qua **Langfuse Public API** thay vì thao tác trên
> UI, nên bằng chứng là JSON trạng thái trước/sau chứ không phải ảnh màn hình.
> Thời điểm: 2026-08-11, khoảng 04:47–04:50 UTC.

## Bối cảnh — vì sao phải làm lại bước này

Khi rà soát trước lúc nộp, R4 phát hiện nhãn `production` **đang nằm trên version 2**
(đổi lúc `04:47:38Z`) và **chưa được rollback**. Đây là mâu thuẫn thật với phần còn lại
của bài nộp:

- 5 trace challenge chạy lúc `04:12` đều ghi `prompt_version=1`, `prompt_label=production`.
- `submission/REPORT.md` mục 4 và 6 đều mô tả `production` đang ở v1 sau rollback.

Nếu để nguyên, người chấm mở Langfuse sẽ thấy `production` trỏ v2 trong khi báo cáo nói
v1. Bước rollback dưới đây vừa lấy được bằng chứng đề yêu cầu, vừa đưa trạng thái live
về khớp với báo cáo.

## Trạng thái TRƯỚC rollback

Nguồn: [`prompt_label_before_rollback.json`](prompt_label_before_rollback.json)

| Version | Labels |
|---:|---|
| 1 | `baseline` |
| 2 | `candidate`, `latest`, **`production`** |

`GET /api/public/v2/prompts/day13-chat?label=production` trả về **version 2**, nội dung
có dòng `Answer style: concise, evidence-first, include one observable signal.`

## Thao tác rollback

```http
PATCH {LANGFUSE_HOST}/api/public/v2/prompts/day13-chat/versions/1
Content-Type: application/json

{"newLabels": ["production"]}
```

Kết quả: `HTTP 200`. Langfuse tự gỡ nhãn `production` khỏi v2 vì mỗi nhãn chỉ trỏ được
tới một version.

## Trạng thái SAU rollback

Nguồn: [`prompt_label_after_rollback.json`](prompt_label_after_rollback.json)

| Version | Labels |
|---:|---|
| 1 | `baseline`, **`production`** |
| 2 | `candidate`, `latest` |

`GET ...?label=production` trả về **version 1**, nội dung trở lại template gốc ba biến:

```text
Feature={{feature}}
Docs={{docs}}
Question={{message}}
```

## Trace kiểm chứng sau rollback

Chạy một request mới sau khi restart API (để xoá cache prompt 60s):

- **Trace ID:** `ae40c34a858bd9966a521e02d89f7143`
- **Session:** `cp2-rollback-verify`
- **Metadata:** `prompt_source=langfuse`, `prompt_version=1`, `prompt_label=production`

Trace này chứng minh rollback có hiệu lực thật tới đường chạy của ứng dụng, không chỉ
đổi trên giao diện quản trị.

## Ghi chú cho R2

Bằng chứng ở đây là JSON từ API. Nếu muốn thêm **ảnh UI** đúng như
`docs/grading-evidence.md` gợi ý, cần chụp màn hình version list lúc `production` còn ở
v2 — nhưng trạng thái đó đã được rollback, nên phải đổi lại rồi rollback lần nữa. Cặp
JSON trước/sau cộng với trace `ae40c34a…` đã thể hiện đủ nội dung mà yêu cầu hướng tới.
