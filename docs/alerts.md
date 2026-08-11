# Alert và Runbook

Mỗi alert phải dựa trên triệu chứng người dùng hoặc SLO, không dựa trực tiếp vào tên implementation nội bộ.

Ba alert dưới đây được thiết kế **sau khi điều tra challenge `day13-k3-observability-v1`**
và cố ý vá đúng những chỗ mà bộ chỉ số mặc định đã để lọt. Bằng chứng:
[`submission/evidence/challenge/NOTES.md`](../submission/evidence/challenge/NOTES.md).

## Alert 1

- **Tên:** `latency_p95_per_feature_breach`
- **Severity:** critical
- **SLI/SLO liên quan:** `latency_p95_ms` — mục tiêu 2000 ms (xem `config/slo.yaml`)
- **Điều kiện và thời gian duy trì:** `p95(latency_ms)` **tách theo từng `feature`**
  vượt 2000 ms, duy trì 5 phút liên tiếp.
- **Ảnh hưởng tới người dùng:** người dùng của feature đó chờ quá 2 giây cho mỗi câu
  trả lời; với luồng hỏi đáp hỗ trợ khách hàng đây là mức bắt đầu bỏ cuộc.
- **Ba bước kiểm tra đầu tiên:**
  1. Mở panel Errors — nếu error rate vẫn 0 thì đây là sự cố latency thuần, không phải lỗi.
  2. Mở panel Latency, xác định **feature nào** vượt ngưỡng (đừng nhìn số tổng).
  3. Mở Langfuse, lọc trace theo feature đó, so latency với traffic nền để khoanh vùng.
- **Mitigation tạm thời:** bật timeout cho retrieval và trả lời không kèm context; nếu
  chỉ một feature hỏng, cân nhắc tắt tạm phần RAG của riêng feature đó.
- **Owner:** Role 3 - Dashboard, SLO & Alert

> **Vì sao tách theo feature, và vì sao là 2000 ms chứ không phải 3000 ms.**
> Trong challenge, `p95` toàn hệ thống chỉ đạt **2651 ms** và `p50` **không nhúc nhích**
> (150 ms → 150 ms) vì chỉ 5/16 request thuộc `refund`. Với ngưỡng mặc định 3000 ms của
> `config/dashboard.yaml`, alert sẽ **im lặng hoàn toàn** trong khi feature `refund` đã
> hỏng và người dùng chờ tới 13 giây. Hai thay đổi — hạ ngưỡng về đúng mức challenge
> quy định (`latency_threshold_ms: 2000`) và tách theo feature — là để alert bắt được
> đúng sự cố mà nhóm vừa điều tra.

## Alert 2

- **Tên:** `error_rate_breach`
- **Severity:** critical
- **SLI/SLO liên quan:** `error_rate_pct` — mục tiêu ≤ 2 % (`config/slo.yaml`,
  khớp threshold panel `errors` trong `config/dashboard.yaml`)
- **Điều kiện và thời gian duy trì:** `count(request_failed) / count(request_received)`
  vượt 2 %, duy trì 5 phút liên tiếp.
- **Ảnh hưởng tới người dùng:** request trả về lỗi 500, người dùng không nhận được câu
  trả lời nào.
- **Ba bước kiểm tra đầu tiên:**
  1. Mở panel Errors, xem `count_by(error_type)` để biết lỗi thuộc loại nào.
  2. Lấy `correlation_id` từ log `request_failed`, tra toàn bộ vòng đời request.
  3. Mở trace tương ứng để xác định span nào ném lỗi (thường là tool hoặc retrieval).
- **Mitigation tạm thời:** nếu lỗi đến từ vector store, tắt RAG và chạy fallback không
  context; nếu đến từ nhà cung cấp LLM, chuyển model dự phòng.
- **Owner:** Role 1 - Logging & PII

## Alert 3

- **Tên:** `synthetic_probe_latency_breach`
- **Severity:** critical
- **SLI/SLO liên quan:** latency đầu-cuối mà người dùng thật cảm nhận (không phải
  `latency_ms` do server tự ghi)
- **Điều kiện và thời gian duy trì:** một synthetic probe bắn **5 request đồng thời mỗi
  phút**; cảnh báo khi `p95` latency đo tại client vượt 5000 ms trong 3 phút liên tiếp,
  **hoặc** khi `probe_latency_p95 > 3 × server latency_p95`.
- **Ảnh hưởng tới người dùng:** người dùng chờ lâu hơn nhiều so với con số hệ thống tự
  báo — đây là dạng sự cố tệ nhất vì dashboard vẫn xanh.
- **Ba bước kiểm tra đầu tiên:**
  1. So `probe_latency_p95` với `latency_p95` của server. Chênh nhiều lần nghĩa là
     request đang **xếp hàng chờ**, không phải xử lý chậm.
  2. Mở Langfuse, xem cửa sổ thời gian của các trace đồng thời. Nếu mỗi trace bắt đầu
     đúng lúc trace trước kết thúc → event loop đang bị chặn.
  3. Soát các lời gọi đồng bộ (`time.sleep`, I/O blocking) nằm trong endpoint `async`.
- **Mitigation tạm thời:** tăng số worker uvicorn để giảm mức độ xếp hàng, đồng thời đẩy
  lời gọi chặn sang threadpool.
- **Owner:** Role 4 - Incident & Demo

> **Vì sao cần alert này.** Đây là bài học đắt nhất từ challenge: **không một log hay
> metric phía server nào phát hiện được sự cố thật.** Đo trên log của 5 request
> challenge, khoảng cách `request_received` → `response_sent` là 2652–2656 ms, khớp gần
> như tuyệt đối với `latency_ms` (2650–2651 ms). Server "thành thật" báo 2.65 giây —
> nhưng client chờ **13281 ms**. Nguyên nhân: `request_received` chỉ được ghi khi handler
> async cuối cùng mới giành được event loop, nên **toàn bộ thời gian xếp hàng nằm ngoài
> tầm nhìn của log**. Chỉ một phép đo từ bên ngoài mới thấy được.
