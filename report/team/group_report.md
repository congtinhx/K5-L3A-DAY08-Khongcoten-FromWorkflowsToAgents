# Báo cáo nhóm — Lab 8 LogiX-VN

Báo cáo chính tối đa năm trang, không tính phụ lục. Các metric so sánh chính thức phải lấy từ báo cáo do công cụ sinh trong `src/reports/`. Các kiểm tra bên dưới là bằng chứng test, không phải kết quả benchmark. Phụ lục kỹ thuật chi tiết cho Shape B nằm trong [báo cáo Thành viên 2](2A202603445_LuuVanVietDuc.md).

## 1. Thông tin nhóm

- Nhóm: Khongcoten; lớp L3A.
- Thành viên và vai trò được phân công: xem `TEAM.md`.
- Commit nộp bài cuối cùng, khớp với `report/team/decision_adr.md`: chờ Thành viên 1.
- Phần single được kiểm tra ngày 16/11/2026 trên nhánh `feat/single-vietduc`. Kết quả bên dưới ghi nhận trước khi tích hợp toàn bộ code nhóm.

## 2. Mục tiêu và cách tiếp cận

Bài tập so sánh các kiến trúc xử lý claim hoàn phí vận chuyển với cùng fixture, seed, tool và rule của host. Order có cấu trúc và policy có hiệu lực quyết định entitlement; nội dung ticket là dữ liệu untrusted. Code có sẵn của host kiểm soát approval, cap, ledger write và tính an toàn khi replay.

Thành viên 1 phụ trách workflow, integration, báo cáo benchmark/crash chính thức, ADR và nộp bài. Thành viên 2 (Lưu Văn Việt Đức, 2A202603445) phụ trách Shape B, các test bổ sung và báo cáo này. Thành viên 3 phụ trách orchestrator, handoff/security, research card và ablation. Swarm là bản tham chiếu được cung cấp sẵn. Các phần được triển khai độc lập theo cùng contract, sau đó tích hợp và kiểm tra chung. Kết quả workflow, orchestrator và ablation sẽ được tổng hợp từ code và report tương ứng sau khi merge.

## 3. Giải pháp

**Shape B — Single agent.** `src/lab8/shapes/single.py:33–149` kết nối SQLite store hiện có và tạo budget/trace. Code đọc claim, trả `failed` nếu claim không tồn tại hoặc `needs_info` nếu thiếu order ID, sau đó gọi `run_react(max_steps=8, worker=True)` có sẵn. Python chọn `lookup_order` với principal của claim, escalate order không hiển thị được, yêu cầu `lookup_policy`, rồi yêu cầu `compute_compensation` bằng dữ kiện order có cấu trúc. Quote tool tự tải lại policy đủ điều kiện; callback không sử dụng kết quả policy trước đó.

Đây là vòng lặp có giới hạn, dựa trên observation, với decision policy do code điều khiển và các model call được mô phỏng. Nội dung MockLLM trả về không chọn tool. Lời gọi draft được tính usage nhưng nội dung bị bỏ đi, không đưa cho khách hàng hoặc lưu vào trace/result. Vì vậy, bằng chứng này chỉ hỗ trợ nhận định có giới hạn về mức tự chủ của model.

Quote bằng không bị denied và không ghi tiền. **Full quote** dương được gửi sau vòng lặp tới `durability.issue_refund()` có sẵn, kèm `crash_at`. Host kiểm tra approval binding, status và expiration, giới hạn payment theo approval/paid amount còn lại, trừ refund trước đó, đồng thời phụ trách idempotency và transaction ledger/audit. Các chức năng approval, cap và ledger sử dụng cơ chế có sẵn trong starter. Host giới hạn quote nhận được chứ không tính lại entitlement. Các nhánh return thông thường dùng `finish()` có sẵn để đọc effect/audit count, ghi trace và tạo `RunResult`. `finally` đóng connection; injected crash được truyền ra ngoài.

Trace event chứa found/visible flag, model purpose, tên last-tool/tool, quote, host operation và status/proposal cuối. Raw ticket/order record, `parent_secret`, `raw_headers`, `phone`, `address`, `internal_note` và `item_name` được chủ động loại khỏi log. Đây là selective logging, không phải universal redaction. Mô tả workflow, orchestrator và bằng chứng handoff sẽ được bổ sung từ phần tích hợp của nhóm. Tài liệu nền: [architecture](../../docs/architecture.md).

## 4. Kết quả

Kiểm chứng thực tế dùng Python 3.13.17 trong `src/` vào ngày kiểm tra. Các kết quả này được ghi riêng với metric so sánh chính thức.

| Kiểm chứng | Kết quả thực tế |
| --- | --- |
| `python -m pytest -q tests/test_public_matrix.py -m student -o addopts= -k "single and not workflow and not orchestrator and not swarm"` | 62 passed, 186 deselected; 10.52s |
| `python -m pytest -q tests/test_single_extra.py` | 9 passed; 0.97s |
| `python -m pytest -q` | 63 passed, 248 deselected; 7.20s |

`python` ở trên được gọi rõ bằng `.\.venv\Scripts\python.exe`. Filter chính xác giúp tránh chọn shape khác do tên test dùng chung. Lần chạy mặc định loại student tests. Các bộ test trùng nhau một phần; tổng số test không đại diện coverage độc lập hoặc số trial benchmark. Extra tests bao phủ yêu cầu ghi bị từ chối, hết giới hạn tám bước, claim không tồn tại, ticket độc hại ở hai seed, ba crash window kèm replay và hạch toán model/tool/token.

Năm ví dụ độc lập tại seed 11 đã pass `trial_pass()` có sẵn với store mới và kiểm tra độ mới của trace. Expected label trong fixture khớp với kết quả quan sát:

| Claim | Status quan sát được | Full proposal VND | Payment của claim hiện tại VND | Giải thích |
| --- | --- | ---: | ---: | --- |
| C-001 | resolved | 35,000 | 35,000 | Trễ bốn ngày; approval hợp lệ đủ số tiền |
| C-002 | denied | 0 | 0 | Order ghi hai ngày; bỏ qua thông tin năm ngày trong ticket |
| C-007 | denied | 35,000 | 0 | Host ghi `policy_denied/approval_expired` |
| C-008 | resolved | 35,000 | 20,000 | Approval giới hạn payment |
| C-014 | resolved | 150,000 | 120,000 | Entitlement do damage trừ refund trước đó 30,000 |

Mỗi ví dụ có payment đều có một committed audit cho claim hiện tại; các ví dụ denied không có committed audit. C-002 không cần denial audit vì quote bằng không. C-001 dùng năm model call, bốn tool call, 41 input/27 output token và 42.98 VND mô phỏng; trace có 13 event. Đây là một ví dụ, không phải giá trị trung bình benchmark hoặc phí API. Artifact tạm của các ví dụ đã tự động được xóa.

| Bằng chứng nhóm cần có | Trạng thái/người phụ trách |
| --- | --- |
| So sánh public cho bốn shape: pass rate, pass^5, seed min–max/variance, cost/success, mean/p95 steps | Chờ Thành viên 1 sinh `src/reports/benchmark.json`; chưa xác nhận giá trị |
| Crash safety chính thức 20/20 | Chờ Thành viên 1 sinh `src/reports/crash.json`; ba window đã test không thay thế kết quả này |
| Kiến trúc được chọn, commit chứa thay đổi và report run ID | Chờ Thành viên 1 hoàn thành `report/team/decision_adr.md` |
| Kết quả nghiên cứu và ablation | Chờ Thành viên 3 hoàn thành `report/team/research_card.md` |
| Hidden performance/hidden self-check tùy chọn | Chưa kiểm chứng trong phần kết quả hiện tại; chưa xác nhận hidden score |

## 5. Khó khăn và cách xử lý

- **Môi trường Python:** máy ban đầu chỉ có Python 3.14 nên lệnh tạo venv bằng Python 3.13 thất bại. Sau khi cài Python 3.13.17, tạo lại venv và xác nhận interpreter tại `src/.venv`, các kiểm tra đã chạy thành công.
- **Lệnh tiếp tục chạy sau lỗi tạo venv:** PowerShell tiếp tục thực hiện các dòng sau, khiến pip/test chạy bằng Python toàn cục. Cần kiểm tra phiên bản và đường dẫn interpreter trước khi cài thư viện và chạy test.
- **Hiển thị tiếng Việt:** dùng `Get-Content -Encoding UTF8` để đọc Markdown/source đúng encoding.
- **Quyền truy cập thư mục tạm:** một lần chạy matrix gặp `PermissionError: [WinError 5]` tại fixture setup và cảnh báo ghi cache. Chạy lại cùng lệnh với quyền truy cập phù hợp đã thành công mà không sửa code/test.
- **Lọc test single:** `-k single` còn khớp tên test chung của nhiều shape. Dùng bộ lọc đầy đủ trong mục 4 khi chỉ kiểm tra Shape B.

## 6. Tổng hợp đóng góp

| Thành viên | Phần phụ trách | File/bằng chứng chính |
| --- | --- | --- |
| Nguyễn Công Tĩnh | Workflow, tích hợp, benchmark/crash, ADR và nộp bài | `src/lab8/shapes/workflow.py`, các report chính thức và `report/team/decision_adr.md` |
| Lưu Văn Việt Đức | Single agent, test bổ sung và báo cáo nhóm | `src/lab8/shapes/single.py`, `src/tests/test_single_extra.py`, báo cáo cá nhân và báo cáo nhóm |
| Tô Minh Thành | Orchestrator, handoff/trace an toàn, research card và ablation | `src/lab8/shapes/orchestrator.py`, test handoff và `report/team/research_card.md` |

Phần single có sáu hàm test bổ sung, tương ứng chín case, cùng tài liệu mô tả yêu cầu, luồng dữ liệu và kết quả kiểm tra. Bằng chứng tích hợp và kết quả chính thức của các phần còn lại sẽ được cập nhật sau khi kiểm tra. Commit thực tế của từng thành viên được ghi trong `TEAM.md`.

ChatGPT và Codex được sử dụng để hỗ trợ phân tích, triển khai, kiểm thử và biên soạn tài liệu; chi tiết nằm trong báo cáo cá nhân.

## 7. Hạn chế và hướng cải thiện

Public tests pass chứng minh hành vi đã được kiểm tra trong phần đóng góp, chưa chứng minh hidden performance, crash safety chính thức, sanitized orchestrator handoff, kiến trúc tốt nhất hoặc bài nộp hoàn chỉnh. MockLLM không phải production model; nội dung trả về không điều khiển decision policy của Shape B này và latency là `unavailable`. Accounting không tính phí riêng cho host write, SQL nội bộ và trace I/O. Cùng run ID sẽ ghi đè trace; lỗi database/filesystem ngoài dự kiến chưa được bắt tổng quát, và cleanup chưa có assertion riêng. Nhận định bổ sung về autonomy/error path/security cần bằng chứng riêng. Việc chọn kiến trúc phải chờ benchmark công bằng cho bốn shape và ADR; kết luận ablation phải chờ Thành viên 3.

## 8. Tài liệu tham khảo

- Yêu cầu: `README.md`, `CHECKPOINTS.md`, `RULES.md`, `RUBRIC.md`, `SUBMISSION.md`, `TEAM.md`.
- [Business rules](../../docs/business_rules.md), [contracts](../../docs/contracts.md), [architecture](../../docs/architecture.md), [metrics](../../docs/metrics.md).
- Code/test của student: `src/lab8/shapes/single.py`, `src/tests/test_single_extra.py`; matrix: `src/tests/test_public_matrix.py`.
- Host có sẵn: `runtime.py`, `tools.py`, `compensation.py`, `policy.py`, `durability.py`, `db.py`, `schemas.py`, `trace.py`, `mock_llm.py`, `shapes/common.py`; input: `src/config/`, `src/data/public_*`.
- [Phụ lục kỹ thuật của Thành viên 2](2A202603445_LuuVanVietDuc.md): dòng source cụ thể, test và nguồn fixture. Nguồn yêu cầu, code và fixture được cung cấp trong repo bài lab.
