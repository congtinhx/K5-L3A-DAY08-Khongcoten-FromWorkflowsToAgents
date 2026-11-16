# Báo cáo cá nhân — 2A202603445_LuuVanVietDuc

## 1. Thông tin thành viên

- Họ tên: Lưu Văn Việt Đức
- MSSV: 2A202603445
- Email: luuvanvietduc@gmail.com
- GitHub: VietDuc
- Nhánh làm việc: `feat/single-vietduc`
- Ngày kiểm tra: 16/11/2026.
- Commit đóng góp: cập nhật sau khi commit.

## 2. Phần việc phụ trách

Phần phụ trách gồm Shape B trong `src/lab8/shapes/single.py`, test bổ sung trong `src/tests/test_single_extra.py` và tổng hợp báo cáo nhóm tại `report/team/group_report.md`.

Shape B kết hợp các thành phần có sẵn của starter: runtime, công cụ tính compensation, kiểm tra approval, ledger và helper tạo result/trace. Trọng tâm là xây dựng luồng xử lý yêu cầu hoàn tiền, tích hợp các thành phần theo đúng contract và kiểm thử các tình huống lỗi.

Phân công chung: Người 1 phụ trách workflow, tích hợp, benchmark, crash suite, ADR và nộp bài; Người 2 phụ trách single và báo cáo nhóm; Người 3 phụ trách orchestrator, handoff/trace an toàn, research card và ablation.

## 3. Đóng góp cụ thể

Đã thay phần stub trong `src/lab8/shapes/single.py` bằng luồng xử lý hoàn chỉnh của `run_claim()`, giữ nguyên chữ ký hàm. Luồng xử lý đọc claim, kiểm tra order theo principal, gọi policy lookup và công cụ tính quote trong vòng lặp tối đa tám bước. Quote dương được chuyển đầy đủ cho host sau vòng lặp; quote bằng không dẫn đến từ chối mà không gọi ghi tiền.

Các nhánh trả kết quả thông thường dùng `done()` và `finish()`, có trace theo contract. Tham số `crash_at` được chuyển tiếp cho host; `InjectedCrash` được truyền ra ngoài. Kết nối SQLite được đóng trong `finally`.

Bổ sung sáu hàm test trong `src/tests/test_single_extra.py`, tạo thành chín trường hợp kiểm thử. Tài liệu ghi lại cách xử lý, nguồn dữ liệu, bằng chứng kiểm thử và các giới hạn của phiên bản hiện tại.

### Ranh giới code/model

`decide()` gọi MockLLM nhưng bỏ chuỗi trả về (`single.py:76–115`). Python phân nhánh theo `last_tool` và observation để chọn action. Đây là vòng lặp có giới hạn, dựa trên observation, với decision policy do code điều khiển và các model call được mô phỏng. Điều này không chứng minh một production LLM tự chọn tool hoặc hiểu ticket mơ hồ.

`done()` cũng bỏ nội dung draft trả về (`single.py:44–63`). Lời gọi vẫn được tính vào usage, nhưng nội dung không được lưu trong SQLite, trace hay `RunResult`, và không được đưa ra làm phản hồi cho khách hàng. `RunResult` không có field chứa thông điệp cho khách hàng (`src/lab8/schemas.py:13–28`); việc chấm điểm dựa trên kết quả có cấu trúc và trạng thái ledger (`docs/contracts.md:7`).

## 4. Bằng chứng

Các đường dẫn bên dưới tính từ gốc repo. Bằng chứng gồm source code, output pytest và năm ví dụ chạy độc lập trên fixture public. Các kết quả này phản ánh phần single trước tích hợp; benchmark và crash suite chính thức của nhóm được tổng hợp riêng.

### Lệnh kiểm chứng và kết quả thực tế

Thư mục chạy: `src/`. Interpreter: `.\.venv\Scripts\python.exe`, đã xác nhận là Python 3.13.17. Các lệnh kiểm tra sử dụng interpreter này:

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests/test_public_matrix.py -m student -o addopts= -k "single and not workflow and not orchestrator and not swarm"
.\.venv\Scripts\python.exe -m pytest -q tests/test_single_extra.py
.\.venv\Scripts\python.exe -m pytest -q
```

| Kiểm tra | Kết quả thành công quan sát được | Ý nghĩa |
| --- | --- | --- |
| Public matrix của Shape B | `62 passed, 186 deselected in 10.52s` | 12 claim chạy một lần × 5 seed, cộng các tình huống retry và crash/resume, chỉ dành cho Shape B |
| Các test bổ sung cho single | `9 passed in 0.97s` | Sáu hàm, gồm hai seed cho injection và ba crash window |
| Host tests mặc định và các test bổ sung | `63 passed, 248 deselected in 7.20s` | Cấu hình mặc định loại student matrix; đây không phải kiểm tra phần triển khai của toàn bộ shape |

Lần chạy matrix trước đó trả về `186 deselected, 2 warnings, 62 errors in 12.36s`. Tất cả case được chọn đều lỗi ở bước fixture setup: pytest không thể liệt kê thư mục tạm Windows hiện có (`PermissionError: [WinError 5]`); thao tác ghi cache cũng cảnh báo bị từ chối truy cập. Chưa có assertion nào của phần triển khai được chạy. Chạy lại cùng lệnh với quyền thực thi rộng hơn đã giải quyết vấn đề môi trường mà không thay đổi source, test, dependency hoặc cấu hình pytest. Các kiểm tra sau đó đều thành công. Lỗi trên thuộc bước chuẩn bị môi trường, không phải assertion thất bại của implementation.

Bảng trên ghi kết quả của lần kiểm tra được lưu trong báo cáo; thời gian có thể khác ở những lần chạy khác. Các bộ test có phần trùng nhau, không được cộng tổng để coi là coverage độc lập. Giữ chính xác filter cho single: chỉ dùng `-k single` cũng khớp với `test_public_single_run_cases` và có thể chọn shape của thành viên khác.

Matrix dùng store mới (`src/tests/test_public_matrix.py:31–34`) và `trial_pass()` có sẵn (`src/lab8/metrics.py:111–149`) để kiểm tra label, sự khớp nhau với ledger, audit, denial audit bắt buộc, độ mới/format của trace và các chuỗi bị cấm trong fixture. Public checks không chứng minh hidden performance hay việc hoàn thành toàn bộ bài nhóm.

### Phụ lục A — Đối chiếu yêu cầu với bằng chứng

“Shape B” chỉ phần triển khai trong `single.py`; “host” chỉ các thành phần có sẵn được gọi tới. Tên extra test tham chiếu tới `src/tests/test_single_extra.py`. Bằng chứng matrix tham chiếu tới `src/tests/test_public_matrix.py:test_public_single_run_cases():46–58`, trừ khi nêu tên hàm khác.

| Yêu cầu/checkpoint | Cách xử lý | Vị trí triển khai | Nguồn thông tin | Bằng chứng test | Hạn chế hoặc việc còn chờ |
| --- | --- | --- | --- | --- | --- |
| Claim không tồn tại; CP2 | Shape B trả `failed/unknown_claim`, proposal 0, qua `done()` | `src/lab8/shapes/single.py:66–70`; `done():44–63` | Host `src/lab8/tools.py:get_claim_view():27–34`; `docs/contracts.md:19` | `test_single_unknown_claim_still_writes_trace():63–67` | Đã kiểm tra trace hợp lệ/không refund; chưa kiểm tra hidden claim |
| Thiếu order ID; CP2 | Shape B trả `needs_info`, proposal 0; không trích ID từ ticket | `src/lab8/shapes/single.py:71–72` | Claim view; `docs/business_rules.md:13` | Matrix C-004, năm seed | Chưa có test riêng kết hợp ticket độc hại với thiếu ID |
| Ownership/principal scope; CP2 | Shape B truyền principal của claim vào lookup; order không hiển thị được thì escalate | `src/lab8/shapes/single.py:87–101,132–133` | Host `src/lab8/tools.py:lookup_order():37–51`; `docs/business_rules.md:14` | Matrix C-005; host `src/tests/test_authorization.py:test_lookup_hides_other_principals_and_sensitive_fields():38` | Đã đọc nhánh lookup không tìm thấy order; extra tests chưa chạy riêng nhánh này |
| Dữ kiện có cấu trúc và ticket; CP1/CP2 | Shape B dùng order đúng scope; không parse ticket để lấy dữ kiện, action hoặc số tiền | `src/lab8/shapes/single.py:91–105` | `docs/business_rules.md:5`; `src/config/autonomy_policy.yaml:23` | Matrix C-002 với năm seed; `test_single_ticket_injection_cannot_change_order_facts():70–85` với 11/55 | Chưa đánh giá security tổng quát cho production LLM; xử lý thông tin mơ hồ còn hạn chế |
| Policy hiện hành/có hiệu lực; CP2 | Shape B yêu cầu policy; quote tool tự tải lại policy đủ điều kiện | `src/lab8/shapes/single.py:101–106`; host `src/lab8/tools.py:76–87,106–114` | Ngày cố định tại `src/config/autonomy_policy.yaml:2`; `src/lab8/compensation.py:24–28`; `docs/business_rules.md:15` | Matrix C-006 dẫn clause cũ; C-002 loại rule cũ cho trễ 1 ngày | Không sử dụng kết quả policy đầu tiên; policy tương lai trong fixture cũng không current, nên extra tests chưa tách riêng điều kiện từ chối theo ngày |
| Compensation do code tính; CP1/CP2 | Shape B gọi tool có sẵn và lưu quote; model không sinh số tiền | `src/lab8/shapes/single.py:102–110,137–140` | Host `src/lab8/tools.py:106–114`; `src/lab8/compensation.py:quote():16–58`; `docs/business_rules.md:9–12,31` | Matrix C-001/C-003/C-009/C-014 và các label khác | Compensation rules/max stacking thuộc code host; write gate không tự tính lại entitlement (`src/config/autonomy_policy.yaml:13,25`) |
| Vòng lặp tối đa tám bước; CP2 | Shape B truyền 8 và xử lý hết bước bằng `failed/step_cap` | `src/lab8/shapes/single.py:118–130` | Host `src/lab8/runtime.py:run_react():58–77`; `docs/architecture.md:21` | `test_single_step_cap_returns_failure_with_trace():53–60` buộc đọc tám lần | Giới hạn đếm số lượt decision; nhánh order hiển thị thông thường cần bốn lượt, không phải tám |
| Read-only tools/từ chối ghi; CP2/CP3 | Shape B dùng `worker=True`; bị từ chối thì trả failure có trace | `src/lab8/shapes/single.py:124–127` | Host `src/lab8/runtime.py:dispatch():30–55`; `src/lab8/handoff.py:19–27` | `test_single_rejected_write_returns_failure_with_trace():41–50` | Runtime thực thi giới hạn; test inject action của callback, không inject nội dung model |
| Refund ngoài vòng lặp; CP2 | Shape B chỉ gọi host sau khi ready và quote dương | `src/lab8/shapes/single.py:129–147` | `docs/architecture.md:21,31`; `src/config/tools.manifest.v1.1.yaml:28–31` | Matrix C-001 và test từ chối ghi | Lời gọi host trực tiếp không phải tool do agent dispatch |
| Full quote và committed amount; CP2 | Shape B truyền và trả full quote, kể cả khi host giảm/từ chối thanh toán | `src/lab8/shapes/single.py:137–147` | `docs/contracts.md:15–18,26`; `docs/business_rules.md:19,29` | Matrix C-007/C-008/C-013/C-014; các ví dụ đã chạy bên dưới | Số tiền thực trả nằm trong `refund_effects`, không phải `proposal_amount` |
| Giao host kiểm tra approval; CP2/CP4 | Shape B gửi mọi quote dương cho host; denial thành denied, conflict thành failed | `src/lab8/shapes/single.py:142–146` | Host `src/lab8/durability.py:79–104`; `src/lab8/policy.py:authorize():63–78` | Matrix C-007; host `src/tests/test_authorization.py:6`; `src/tests/test_order_cap_and_approval_binding.py:99,112` | Approval thiếu/bị thu hồi/gắn sai claim có host coverage, chưa có case single mới cho từng loại; Approval engine có sẵn trong starter |
| Per-order caps/refund trước đó; CP2/CP3 | Shape B không trừ trước; host trừ refund của claim khác và kiểm tra lại tổng trong transaction | `src/lab8/shapes/single.py:143`; host `src/lab8/policy.py:32–41,80–92`; `src/lab8/durability.py:120–127` | `docs/business_rules.md:18,27–29`; fixture `prior_refunds` | Matrix C-013/C-014; host tests `src/tests/test_order_cap_and_approval_binding.py:50,73` | Shape B không gọi refund-history tool; host phụ trách kiểm tra tổng/concurrency |
| Retry/idempotency/crash; CP3 | Shape B chuyển tiếp `crash_at` và để `InjectedCrash` truyền ra ngoài; host phụ trách replay và tính duy nhất của effect/audit/checkpoint | `src/lab8/shapes/single.py:143–149`; host `src/lab8/durability.py:26–31,107–184`; `src/lab8/db.py:53–70` | `docs/contracts.md:27`; `docs/business_rules.md:20–21` | Matrix `test_t11_retry_keeps_one_refund():63`, `test_t12_crash_before_checkpoint_does_not_double_pay():81`; extra `test_single_all_crash_windows_resume_once():88–98` | Ba window chưa thay thế crash suite chính thức 20/20; replay vẫn qua authorization hiện tại; số tiền được cho phép thay đổi có thể gây conflict |
| RunResult/trace mới; CP2 | Shape B dùng `done()`/`finish()` trên các return thông thường; run ID xác định | `src/lab8/shapes/single.py:40–63`; host `src/lab8/shapes/common.py:finish():38–69`; `src/lab8/trace.py:23–31` | `docs/contracts.md:9,23–25,38–43`; `src/lab8/schemas.py:13–35,68–69` | Matrix kiểm tra độ mới; test unknown/rejection/cap kiểm tra tính hợp lệ | Crash ném exception thay vì return và có thể không ghi trace mới; không bắt tổng quát exception DB/I/O ngoài dự kiến; trùng run ID sẽ ghi đè trace |
| Nội dung trace/bỏ dữ liệu nhạy cảm; CP3/CP4 | Shape B ghi flag, purpose, tên tool/operation, quote và status/proposal cuối; không ghi observation | `src/lab8/shapes/single.py:51–52,68,85,96,109,114,142` | `docs/contracts.md:41–45`; adapters `src/lab8/tools.py:12–20,27–51` | Matrix quét chuỗi cấm (`src/lab8/metrics.py:145–148`); injection quét artifact | Chủ động bỏ raw ticket/order, `parent_secret`, `raw_headers`, `phone`, `address`, `internal_note`, `item_name`; selective logging không phải universal redaction; không ghi giải thích policy/approval chi tiết |
| Hạch toán model/tool/token/cost; CP2/CP5 | Shape B tính lần đọc đầu; runtime tính dispatched reads; MockLLM tính decision/draft | `src/lab8/shapes/single.py:45–50,66,79–84`; host `src/lab8/mock_llm.py:31–50`; `src/lab8/runtime.py:42`; `src/lab8/schemas.py:38–57` | `src/config/pricing.yaml:1–7`; `docs/metrics.md:3–5,15` | `test_single_counts_model_calls_for_react_and_draft():101–107`; kết quả C-001 bên dưới | VND mô phỏng, latency unavailable; không tính phí riêng cho host write/SQL nội bộ/finish reads/trace I/O |
| Database cleanup | Shape B đóng connection trong `finally` sau return thông thường và khi host crash truyền ra ngoài | `src/lab8/shapes/single.py:65,148–149` | Connection của host `src/lab8/db.py:connect():75–79` | Đọc source; các nhánh thường/crash được chạy gián tiếp | Chưa có close-spy assertion; khởi tạo connection/Budget/Trace nằm trước try được bảo vệ, nên cleanup khi khởi tạo lỗi chưa được kiểm chứng |

### Phụ lục B — Luồng xử lý và lưu trữ thực tế

1. **Khởi tạo.** Caller cung cấp claim ID, seed, đường dẫn SQLite hiện có và crash window tùy chọn. Test nạp public fixtures qua `db.init_store()` (`src/lab8/db.py:82–199`); bản thân `run_claim()` không nạp dữ liệu ban đầu. Hàm kết nối và tạo budget/trace cục bộ với ID `R-single-{claim_id}-s{seed}`. Shape chưa ghi SQLite hoặc file trace ở bước này.
2. **Đọc claim.** `get_claim_view()` đọc claim ID, principal, order ID, ticket và thêm `found`. Ticket nằm cục bộ, là dữ liệu untrusted, không được dùng cho decision/prompt. View không chứa secret, header hay chi tiết approval. Tính thêm một tool call; trace chỉ ghi found flag. Nhánh claim không tồn tại/thiếu order ID trả qua `done()` với proposal bằng không, không ghi refund/audit.
3. **Lượt 1: yêu cầu order.** Observation ban đầu chứa claim. Python gọi MockLLM với claim ID/tên tool trước đó, bỏ nội dung trả về và chọn `lookup_order` có kiểm tra scope. Runtime thực thi read-only access, tính một tool call và cung cấp observation tiếp theo. Trace ghi purpose/tên tool, không ghi argument/result. SQLite chỉ được đọc.
4. **Lượt 2: kiểm tra visibility.** Nếu order không tồn tại hoặc ngoài scope, lưu lý do vào state cục bộ và trả final nội bộ `escalated`. Nếu hợp lệ, `state["order"]` chứa order ID, status, delay, shipping fee, paid amount, verified damage và carrier, không chứa field nhạy cảm. Trace ghi visibility. Python yêu cầu policy lookup.
5. **Lượt 3: yêu cầu quote.** Policy observation chứa `as_of` cố định và các policy hiện hành/có hiệu lực, nhưng callback không lưu hoặc diễn giải kết quả đó. Python chuyển sang `compute_compensation(state["order"])`. Tool của host tải lại policy và gọi `compensation.quote()`. Ngày áp dụng là **2026-11-15**, không phải ngày kiểm tra. Các rule hiện hành, đã có hiệu lực quyết định entitlement cho shipping/damage và cách stacking theo max-of-eligible. Không ghi SQLite.
6. **Lượt 4: kết thúc vòng lặp.** Quote observation chứa amount, reason, clause ID và parts. Shape B lưu toàn bộ quote cục bộ, chỉ ghi amount vào trace và trả `ready` nội bộ; `ready` không bao giờ trở thành `RunResult.status`. Rejection, hết giới hạn bước hoặc kết quả vòng lặp không hợp lệ trở thành failure có cấu trúc. Mỗi lượt callback thông thường đều gọi và tính usage MockLLM, nhưng bỏ nội dung trả về.
7. **Gọi host sau vòng lặp.** Quote bằng không trả denied, không gọi host và không cần denial audit. Quote dương được ghi trace và truyền đầy đủ vào `issue_refund()`, kèm fault window. Shape B không tự trừ history hoặc áp approval cap.
8. **Authorization/ghi tại host.** Host tải lại claim/order, kiểm tra scope và binding/status/expiration/amount của đúng approval được tham chiếu. Host trừ refund của claim khác và giới hạn payment theo approval cùng phần paid amount còn lại. Khi từ chối, host thêm audit `policy_denied` có idempotency. Khi thanh toán mới, host ghi ledger effect và `refund_committed` trong cùng transaction, kiểm tra lại tổng theo order dưới `BEGIN IMMEDIATE`. Checkpoint được ghi riêng sau đó. Replay khớp sẽ dùng lại effect; số tiền được authorization hiện tại khác trước sẽ gây conflict và được audit. Host giới hạn entitlement được truyền vào, không tính lại entitlement từ policy. Injected crash được truyền ra caller.
9. **Hoàn tất và đóng connection.** `done()` gọi draft MockLLM chỉ với status/proposal, bỏ nội dung trả về và ghi model/decision event vào trace. `finish()` có sẵn đọc effect/audit count của claim hiện tại, ghi JSON trace UTF-8 và tạo `RunResult`: định danh, status cuối, full proposal, effect/count thực tế, model/tool count, token, cost đã làm tròn, trace path và reason tùy chọn. Không lưu bền vững conversation/state của agent, quote hay draft cho khách hàng; refund checkpoint thuộc host. `finally` đóng SQLite. Lần chạy bị crash bỏ qua bước finish thông thường.

Kết quả quan sát C-001 với seed 11: bốn decision trong vòng lặp cộng một draft = **5 model calls**; lần đọc ban đầu cộng ba dispatched reads = **4 tool calls**. Usage là **41 input / 27 output tokens**. Cost là `4 × 10 + 41/1000 × 20 + 27/1000 × 80 = 42.98` VND mô phỏng. `Budget.steps` nội bộ bằng 9; trace có **13 events**. Metric `steps` của benchmark đếm trace event, không đếm lượt vòng lặp hay budget step. Policy lookup thứ hai bên trong tool không phải một tool được dispatch/tính phí thêm. Không đo latency của model thật.

### Phụ lục C — Ví dụ từ public fixtures

Expected label lấy từ `src/data/public_claims.jsonl` tại các dòng 1, 2, 7, 8 và 14. Input được đọc qua các field an toàn đã chọn, không dump giá trị nhạy cảm. Việc đọc code/dữ liệu dẫn tới các kết quả suy luận bên dưới; sau đó từng ví dụ thực sự được chạy với seed 11 trong public-fixture store mới riêng biệt và pass `trial_pass()` có sẵn, bao gồm kiểm tra độ mới của trace. Store/trace tạm của ví dụ đã tự động được xóa; đây là phần minh họa, không phải kết quả benchmark chính thức.

| Claim và nguồn fixture | Input và giải thích qua kiểm tra code/dữ liệu | Kỳ vọng trong fixture | Kết quả quan sát thực tế |
| --- | --- | --- | --- |
| C-001; `src/data/public_world_state.json:19` order O-107, `:234` approval | Giao trễ 4 ngày; shipping 35,000, paid 250,000; approval hợp lệ 35,000 VND | resolved; proposal/payment 35,000; committed count 1 | Đúng kỳ vọng; một checkpoint, không có denial audit |
| C-002; world `:33` order O-202, `:241` approval | Ticket khai trễ 5 ngày; order đã giao ghi 2 ngày, shipping 20,000, không có verified damage. Rule hiện hành yêu cầu 3 ngày | denied; proposal/payment 0; committed count 0 | `denied/no_entitlement`; không có effect/audit/checkpoint |
| C-007; world `:103` order O-909, `:262` approval | Trễ 4 ngày cho quote 35,000; approval có status valid nhưng hết hạn 2020-01-01, trước ngày cố định | denied; proposal 35,000, payment 0; cần denial audit | `denied/approval_expired`; không có effect/committed audit/checkpoint; một `policy_denied` với lý do đó |
| C-008; world `:89` order O-808, `:269` approval | Trễ 4 ngày cho quote 35,000; approval chỉ cho phép 20,000 | resolved; proposal 35,000, payment 20,000; committed count 1 | Đúng kỳ vọng; một checkpoint, không có denial audit |
| C-014; world `:131` order O-515, `:311` approval, `:326` history | Shipping 30,000 và verified damage 150,000 so với paid 200,000; entitlement lớn nhất 150,000. Đã refund 30,000; approval 150,000 | resolved; proposal 150,000, payment mới 120,000; committed count của claim hiện tại 1 | Đúng kỳ vọng; một checkpoint; tổng theo order 150,000 gồm history |

Các policy record trong world bắt đầu tại `src/data/public_world_state.json:161` (rule hiện hành tháng 11/2026), `:191` (rule đã bị thay thế), `:212` (rule tương lai). Run ID của ví dụ: `R-single-C-001-s11`, `R-single-C-002-s11`, `R-single-C-007-s11`, `R-single-C-008-s11`, `R-single-C-014-s11`. Các ID xác định này nhận diện lời gọi, không phải benchmark report hoặc artifact đã commit.

### Phụ lục D — Giải thích từng test bổ sung

Mỗi case dùng database public mới. Dữ liệu thay đổi trong test chỉ tác động store tạm, không sửa fixture trong `src/data/`.

| Hàm trong `src/tests/test_single_extra.py` | Injection/thay đổi | Assertion | Coverage bổ sung |
| --- | --- | --- | --- |
| `test_single_rejected_write_returns_failure_with_trace():41` | `force_action()` giữ runtime thật nhưng thay callback bằng yêu cầu ghi `issue_refund` | failed/tool_rejected; trace hợp lệ; worker=True; không refund/committed audit | Kiểm tra single integration và báo lỗi rejection ngoài các action public thông thường; không kiểm tra nội dung model |
| `test_single_step_cap_returns_failure_with_trace():53` | Callback liên tục yêu cầu `lookup_policy` qua runtime thật | failed/step_cap; max và callback count đều bằng 8; trace hợp lệ; không refund/committed audit | Buộc hết bước, kiểm tra cap cấu hình và failure trả về |
| `test_single_unknown_claim_still_writes_trace():63` | Chạy claim ID không tồn tại | failed/unknown_claim; trace hợp lệ; không refund/committed audit | Kiểm tra early return của unknown claim, chưa có trong matrix dùng ID đã biết |
| `test_single_ticket_injection_cannot_change_order_facts():71` | Sửa ticket C-002 bằng chỉ dẫn bỏ qua policy, số tiền/độ trễ quá lớn và synthetic canary marker; seed 11/55 | denied, proposal 0; không có canary prefix trong result/trace artifact; không refund/committed audit | Bổ sung chỉ dẫn tấn công/marker rõ ràng vào coverage mâu thuẫn dữ kiện đã có |
| `test_single_all_crash_windows_resume_once():91` | C-012 tại before_effect, after_effect_before_checkpoint, after_checkpoint; resume rồi replay | Crash phải truyền ra ngoài; các lần sau resolved; replay có một effect/committed audit, amount 35,000 | Matrix T12 chỉ kiểm tra window giữa; bổ sung hai window ngoài và thêm replay; không thay thế suite chính thức 20 điểm |
| `test_single_counts_model_calls_for_react_and_draft():101` | Chạy C-001 thông thường; đọc trace | Năm model event bằng model_calls; bốn tool call; input/output token dương | Kiểm tra chính xác call accounting của Shape B ngoài assertion về kết quả nghiệp vụ; test chưa assert chính xác phép tính token/pricing |

Helper không phải test: `assert_no_refund():13–19` đọc ledger/audit và đóng connection; `force_action():22–38` monkeypatch callback nhưng giữ cơ chế thực thi giới hạn của runtime. Sau khi mở rộng parameter: 1+1+1+2+3+1 = **9 cases**, không phải chín hàm. Callback bị thay thế bỏ qua các decision call thông thường của student; model count trong các case đó không đại diện usage của nhánh thông thường.

## 5. Công cụ AI đã dùng

Sử dụng ChatGPT và Codex để hỗ trợ phân tích yêu cầu, triển khai, kiểm thử và biên soạn tài liệu. Kết quả được kiểm tra bằng cách đối chiếu source code, luật nghiệp vụ, output pytest và kết quả ledger/trace. Các số liệu benchmark, hidden, crash suite chính thức và ablation chỉ được bổ sung khi có bằng chứng tương ứng.

## 6. Tự đánh giá

Bằng chứng hỗ trợ việc Shape B đáp ứng public contract đã kiểm tra, tích hợp read-only có giới hạn, giao tính quote xác định cho code, giao host authorization cho quote dương, ghi trace ở return thông thường, hạch toán usage và xử lý các nhánh retry/crash đã test. Kết quả này chưa xác nhận điểm nhóm hoặc toàn bộ yêu cầu hidden.

Hạn chế gồm tool selection do code điều khiển, không dùng nội dung model/không đưa draft ra ngoài, không dùng policy observation đầu tiên, trace ít chi tiết và bị ghi đè khi trùng ID, thiếu cleanup assertion riêng và chưa bao phủ đầy đủ error path. Exception database/I/O bất kỳ có thể truyền ra ngoài; phần khởi tạo trước `try` chưa được cleanup assertion bao phủ. Cost là mô phỏng; latency unavailable. Khả năng chọn tool bằng mô hình thực cần được thiết kế và đánh giá riêng.

Phần single đã có bằng chứng kiểm thử public. Báo cáo nhóm sẽ được cập nhật sau khi tích hợp workflow và orchestrator, chạy lại test toàn nhóm và nhận các report chính thức. Commit đóng góp được cập nhật bằng hash thực tế sau khi commit; chưa kết luận về hidden performance.

Lời trình bày demo: “Em triển khai Shape B và các test bổ sung. Python chọn read tool dựa trên observation trong giới hạn tám bước. MockLLM mô phỏng lời gọi và cost; nội dung trả về không chọn tool, còn draft được bỏ đi. Các tool có sẵn của host dùng order có cấu trúc và policy hiện hành để tính full quote. Host kiểm tra approval, trừ refund trước đó và commit an toàn. C-008 có quote 35,000 nhưng trả 20,000; C-014 có quote 150,000 và trả 120,000. Public matrix pass 62 case và các test bổ sung của em pass chín case. Kết luận về benchmark nhóm, crash chính thức và hidden cần bằng chứng riêng.”
