# Checkpoint 1 — Logging & PII

- Owner: Nguyễn Chí Hướng — 2A202601203
- Branch: `logging-and-pii`
- Technical commit: [`5d55476`](https://github.com/huylq-at-work/Day13-K3-D305-A1/commit/5d55476cb72a0ddd8f7782b3a3a764a9a3dc826d)
- Validator: [`checkpoint-1-validate-logs.txt`](checkpoint-1-validate-logs.txt) — 100/100
- Test suite: 27 passed

## Correlation ID và metadata

Hai event của cùng một request dùng chung `correlation_id`; response body và header `x-request-id` cũng trả lại ID này theo định dạng `req-<8 hex>`.

```json
{"service":"api","event":"request_received","correlation_id":"req-9e856561","user_id_hash":"4d14d5d4f719","session_id":"s09","feature":"qa","model":"claude-sonnet-4-5","env":"dev","payload":{"message_preview":"What is the policy for PII and credit card [REDACTED_CREDIT_CARD]?"}}
{"service":"api","event":"response_sent","correlation_id":"req-9e856561","user_id_hash":"4d14d5d4f719","session_id":"s09","feature":"qa","model":"claude-sonnet-4-5","env":"dev","latency_ms":151,"tokens_in":36,"tokens_out":154,"cost_usd":0.002418,"quality_score":0.9}
```

## PII redaction

Input thử nghiệm gồm email, số điện thoại Việt Nam và số thẻ mẫu. Log chỉ giữ placeholder, không giữ giá trị nguyên văn:

```json
{"event":"request_received","payload":{"message_preview":"What is your refund policy? My email is [REDACTED_EMAIL]"}}
{"event":"request_received","payload":{"message_preview":"Here is my phone [REDACTED_PHONE_VN], what should be logged?"}}
{"event":"request_received","payload":{"message_preview":"What is the policy for PII and credit card [REDACTED_CREDIT_CARD]?"}}
```

PII processor chạy sau exception/stack rendering và ngay trước khi JSON được ghi, đồng thời scrub đệ quy các chuỗi ở context, payload, list và object lồng nhau.

## Phạm vi source và kiểm thử

- `app/middleware.py`: validate/sinh/propagate correlation ID và cô lập context.
- `app/main.py`: bind metadata dùng chung cho toàn bộ log của request.
- `app/logging_config.py`: scrub đệ quy trước khi JSON renderer ghi log.
- `tests/test_logging_checkpoint.py`, `tests/test_pii.py`: kiểm tra correlation ID,
  enrichment và các loại PII yêu cầu.
