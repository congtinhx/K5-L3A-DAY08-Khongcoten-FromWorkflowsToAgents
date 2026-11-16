# Decision record

Điền sau dấu `:` trên cùng dòng, không xóa nhãn. Giảng viên và `python -m lab8.check_submission` (chạy trong `src/`) đọc các dòng này bằng máy. Không đổi tên hay dời file này khỏi `report/team/`.
`Shape chọn` phải là đúng một trong: `workflow`, `single`, `orchestrator`, `swarm`. Đây là shape được chấm cổng hidden.

- Shape chọn: workflow
- Commit hash: 6d6c877
- Run id dẫn chứng: R-workflow-C-002-s55 (swarm cùng claim, cùng seed: R-swarm-C-002-s55 trả resolved 20000 thay vì denied)
- Pass rate / pass^5 / seed min-max / variance: 1.000 / 1.000 / 1.000–1.000 / 0.000000 (14 claim public × 5 seed = 70 trial, src/reports/benchmark.json)
- Cost per success (mô phỏng, VND): 27.86 (single 39.19, orchestrator 46.43, swarm 49.57)
- Crash safety: 20/20 (src/reports/crash.json)
- Secret leak / approval bypass: 0 / 0 (70/70 trial lý do ok; trace không chứa CANARY_SECRET_; refund chỉ ghi qua durability.issue_refund)

Ví dụ một dòng đã điền: `- Shape chọn: workflow`, `- Crash safety: 20/20 (src/reports/crash.json)`.

## Vì sao shape này

Cả bốn shape chạy trên cùng corpus (14 claim public), cùng 5 seed (11, 22, 33, 44, 55) và cùng bảng giá trong `src/reports/benchmark.json`. Workflow, single và orchestrator cùng đạt pass rate 1.000, pass^5 1.000, variance 0. Swarm đạt 0.986, pass^5 0.929, vì ở seed 55 nó tin số ngày trễ ghi trong ticket C-002 và hoàn 20.000 thay vì từ chối. Khi độ đúng đã bằng nhau, nhóm chọn shape ít tự chủ nhất: workflow có cost/success thấp nhất (27.86 VND mô phỏng, rẻ hơn single 29%, orchestrator 40%, swarm 44%), không gọi model lần nào (mean model calls = 0), mean steps 4.43, p95 steps 5. Mọi quyết định tiền đều nằm trong code (`compute_compensation` rồi `durability.issue_refund`), nên kết quả không phụ thuộc seed.

## Có đáng đổi lấy multi-agent không

Không. Trên corpus public, multi-agent (orchestrator, swarm) không tăng pass rate so với workflow mà tốn hơn 67–78% chi phí mỗi lần thành công. Swarm còn thêm variance giữa các seed. Nhóm vẫn giữ workflow kể cả khi một shape multi-agent nhỉnh hơn vài điểm pass, nếu đổi lại cost và variance cao hơn, vì lỗi ở đây là lỗi tiền thật và cần lặp lại được. Quyết định sẽ đảo lại nếu xuất hiện loại claim mà luật cố định không xử lý được: ticket phải hiểu ngôn ngữ tự nhiên để lấy dữ kiện không có trong DB (ví dụ mô tả hư hỏng cần phân loại), hoặc nhiều nguồn dữ liệu cần điều tra song song. Khi đó nên thêm một bước model chỉ đọc và soạn chữ, còn tiền và lệnh ghi vẫn để code quyết.

## Trace và bằng chứng

Trace workflow (ghi bằng `lab8.trace.Trace`, file `traces/<run_id>.json`) có các event: `claim` (chỉ `claim_id` và cờ `has_order_id`), `lookup_order` (cờ `visible`, `reason`, và order view đã qua allowlist `ORDER_FIELDS`), `quote` (số tiền, lý do, clause_ids), `issue_refund` (ok, reason, conflict), `crash` khi có crash cài sẵn, và `decision` (status, proposal_amount, reason). Cố ý không ghi: ticket gốc (có thể chứa câu lệnh độc hại hoặc dữ liệu khách), `principal_id`, `parent_secret`, `raw_headers`, SĐT, địa chỉ, tên hàng, internal note. Lý do: trace là ranh giới bảo mật, grader quét file này, và chỉ field đã qua allowlist mới được ghi. Mọi nhánh return, kể cả trả sớm và crash, đều ghi trace, nên scanner luôn có file để quét. Nếu trace nằm ngoài chỗ scanner quét được, đội security không thể chứng minh hệ thống sạch; vì vậy nhóm không ghi log ở nơi khác, không in ra stdout, và dùng test `tests/test_workflow_extra.py` để khẳng định trace không có `CANARY_SECRET_`.

## Giới hạn

MockLLM không phải model sản xuất; cost là VND mô phỏng, không phải hóa đơn API. Latency để `unavailable`. Số liệu chỉ trên 14 claim public; bộ hidden 40 claim chưa chạy được ở phía nhóm. Không sửa JSON cho đủ 0.75: `benchmark.json` và `crash.json` do `lab8.benchmark` và `lab8.crash_test` sinh ra, không chỉnh tay.