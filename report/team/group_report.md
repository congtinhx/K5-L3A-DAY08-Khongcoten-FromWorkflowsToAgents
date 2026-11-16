# Báo cáo nhóm — Lab 8 LogiX-VN

## 1. Thông tin nhóm

- Tên nhóm: Khongcoten
- Lớp: L3A
- Thành viên và phân công: xem `TEAM.md`.
- Ngày tổng hợp: 16/11/2026.
- Repo: `congtinhx/K5-L3A-DAY08-Khongcoten-FromWorkflowsToAgents`.
- Nhánh tích hợp: `main`.
- Kiến trúc được chọn: `workflow`, theo `report/team/decision_adr.md`.
- Commit dẫn chứng hiện ghi trong ADR: `6d6c877`.

Báo cáo ghi nhận kết quả sau khi tích hợp workflow, single và orchestrator. Số liệu benchmark/crash lấy từ JSON do công cụ sinh trong `src/reports/`; kết quả pytest được trình bày riêng. Phụ lục kỹ thuật của Shape B nằm trong [báo cáo cá nhân](2A202603445_LuuVanVietDuc.md).

## 2. Mục tiêu và cách tiếp cận

Bài toán xử lý claim hoàn phí vận chuyển của LogiX-VN bằng bốn kiến trúc: workflow, single agent, orchestrator và swarm tham chiếu. Mục tiêu là chọn kiến trúc ít tự chủ nhất nhưng vẫn đáp ứng yêu cầu, dựa trên độ đúng, độ ổn định và chi phí mô phỏng.

Order có cấu trúc và policy hiện hành là nguồn quyết định số tiền đủ điều kiện hoàn. Ticket là dữ liệu không đáng tin cậy. Tiền do code tính; approval, cap, ledger và chống ghi trùng được kiểm soát bởi host có sẵn.

Ba shape được triển khai độc lập theo cùng contract, sau đó tích hợp và kiểm tra chung. Benchmark giữ cùng corpus, seed, MockLLM, bảng giá và evaluator; mỗi trial có SQLite mới để tránh hưởng kết quả của lần chạy trước.

## 3. Giải pháp

### 3.1. Shape A — Workflow

Triển khai tại `src/lab8/shapes/workflow.py`, chạy theo chuỗi bước cố định: đọc claim bằng `get_claim_view()`, kiểm tra order ID, tra order theo principal, tính quote bằng `compute_compensation()` rồi gọi host nếu quote dương.

Claim không tồn tại trả `failed`; thiếu mã đơn trả `needs_info`; order không thấy được trả `escalated`. Quote bằng 0 trả `denied` mà không gọi ghi refund. Quote dương được truyền đầy đủ cho `issue_refund()`; kết quả được tạo bằng `finish()`.

Workflow không gọi MockLLM trong phiên bản hiện tại. Dữ kiện trong ticket không được dùng để sửa order hoặc tính tiền. Khi gặp `InjectedCrash`, chương trình ghi trace rồi ném lại exception; lỗi thông thường được chuyển thành `failed` có ghi loại lỗi.

### 3.2. Shape B — Single agent

Triển khai tại `src/lab8/shapes/single.py`, sử dụng `run_react(max_steps=8, worker=True)`. Callback chọn tool theo observation: `lookup_order`, `lookup_policy`, rồi `compute_compensation`. Sau vòng lặp, code mới gọi host ghi refund.

Python điều khiển lựa chọn tool. MockLLM mô phỏng lời gọi và usage; chuỗi trả về không quyết định hành động. Lượt gọi draft được tính chi phí nhưng nội dung chưa được lưu hoặc trả cho khách hàng. Kết quả policy lookup đầu tiên chưa được callback sử dụng trực tiếp; công cụ compensation tự đọc lại policy phù hợp.

Các trường hợp tool bị chặn, hết tám bước hoặc kết quả vòng lặp không hợp lệ được trả thành `failed` có trace. Các nhánh trả kết quả thông thường dùng `done()` và `finish()`. `crash_at` được chuyển tiếp và `InjectedCrash` được truyền ra ngoài.

### 3.3. Shape C — Orchestrator

Triển khai tại `src/lab8/shapes/orchestrator.py`. Orchestrator đọc các trường claim cần thiết và tạo handoff bằng `make_handoff()`, chỉ cấp các tool đọc: `lookup_order`, `lookup_policy`, `compute_compensation`.

`run_readonly_investigators()` thực hiện tra cứu và trả kết quả cho orchestrator. Investigator không có tool ghi. Orchestrator nhận quote và gọi `issue_refund()` nếu quote dương. Các trường hợp thiếu order ID, order ngoài phạm vi hoặc thiếu kết quả compensation được trả thành trạng thái tương ứng.

Trace ghi handoff đã sanitize, trạng thái truy cập order và quote; không ghi parent context hoặc nguyên bản ghi claim/order. Phiên bản này điều phối bằng code và không gọi MockLLM.

### 3.4. Ranh giới dữ liệu và quyền ghi

Cả ba shape giữ nguyên chữ ký `run_claim()` và truyền quote đầy đủ cho host, không tự trừ khoản đã hoàn trước đó. Host kiểm tra approval đúng claim, trạng thái, thời hạn và cap; trừ refund của claim khác trên cùng đơn trước khi quyết định khoản ghi mới.

Ledger effect và audit `refund_committed` được ghi trong cùng transaction. Retry khớp sử dụng lại effect đã ghi; số tiền được phép khác trước có thể dẫn đến conflict. Host giới hạn quote nhận được, không tự tính lại entitlement từ policy.

Các return thông thường dùng `finish()` để đọc effect/audit thực tế, ghi trace và tạo `RunResult`. Kết nối SQLite được đóng trong `finally`. Các trường `parent_secret`, `raw_headers`, `phone`, `address`, `internal_note`, `item_name` không được ghi vào trace. Workflow ghi order view qua allowlist; single ghi trường chọn lọc; orchestrator ghi handoff đã sanitize.

## 4. Kết quả

### 4.1. Kiểm thử sau tích hợp

Các kiểm tra được chạy trên Windows, Python 3.13.17, venv tại `src/.venv`. Thư mục thực thi là `src/`.

| Kiểm tra | Kết quả |
| --- | --- |
| `python -m pytest -q` | `75 passed, 248 deselected in 11.95s` |
| `python -m pytest -q tests/test_public_matrix.py -m student -o addopts=` | `248 passed in 30.92s` |

Bộ mặc định kiểm host và test bổ sung. Ma trận student kiểm bốn shape trên các case public, gồm nghiệp vụ, retry và crash/resume. Hai bộ có mục đích khác nhau; không dùng tổng test thay metric benchmark.

Riêng single trước tích hợp đạt 62 case student và chín case bổ sung. Test bổ sung kiểm tool ghi bị chặn, hết tám bước, claim không tồn tại, ticket đối kháng, ba cửa sổ crash và usage accounting.

### 4.2. Benchmark bốn kiến trúc

Benchmark dùng 14 claim public và năm seed `11,22,33,44,55`: 70 trial mỗi shape, tổng cộng 280 trial. Ngày nghiệp vụ cố định là `2026-11-15`.

```powershell
python -m lab8.benchmark --shapes workflow,single,orchestrator,swarm --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/benchmark.json
```

Nguồn số liệu: `src/reports/benchmark.json`; các số thập phân dưới đây được làm tròn khi trình bày.

| Shape | Pass rate | Pass^5 | Variance | Seed min–max | Cost/success (VND mô phỏng) | Mean steps | p95 steps |
| --- | ---: | ---: | ---: | --- | ---: | ---: | ---: |
| Workflow | 1.000 | 1.000 | 0.000000 | 1.000–1.000 | 27.86 | 4.43 | 5 |
| Single | 1.000 | 1.000 | 0.000000 | 1.000–1.000 | 39.19 | 11.64 | 13 |
| Orchestrator | 1.000 | 1.000 | 0.000000 | 1.000–1.000 | 46.43 | 2.79 | 3 |
| Swarm | 0.986 | 0.929 | 0.000816 | 0.929–1.000 | 49.57 | 2.80 | 3 |

Workflow, single và orchestrator đạt 70/70 trial. Swarm đạt 69/70, lỗi một trial tại C-002, seed 55: trả `resolved` thay vì `denied`. Đây là weakness có sẵn trong swarm tham chiếu: ticket nói trễ năm ngày nhưng order ghi hai ngày; ở seed chia hết cho 5, swarm có thể dùng số ngày trong ticket.

Theo ADR, nhóm chọn workflow vì đạt cùng pass rate/pass^5 với single và orchestrator nhưng cost/success thấp nhất, không gọi model và không có biến động giữa năm seed trên bộ public. Run ID minh họa: `R-workflow-C-002-s55`; đối chứng là `R-swarm-C-002-s55`.

Chi phí là mô phỏng, không phải hóa đơn API. `steps` đếm event trong trace, không phải thời gian chạy hoặc số lượt suy luận. Các shape ghi trace khác độ chi tiết nên ít event hơn không đồng nghĩa chạy nhanh hơn. Latency là `unavailable`.

### 4.3. Crash safety

```powershell
python -m lab8.crash_test --count 20 --out reports/crash.json
```

Kết quả tại `src/reports/crash.json`: **20/20 kịch bản đạt**, `crash_safety = 20/20`.

Suite chính thức kiểm host và swarm tham chiếu. Retry/crash của ba shape nhóm viết được kiểm thêm qua T11/T12 trong ma trận student. Single còn có test riêng cho ba điểm crash: trước effect, sau effect trước checkpoint và sau checkpoint.

### 4.4. Ví dụ xử lý claim

Các ví dụ public với seed 11, sử dụng store mới, khớp nhãn qua `trial_pass()` trong lần kiểm tra đã ghi nhận:

| Claim | Trạng thái | Quote đầy đủ (VND) | Khoản hoàn mới (VND) | Giải thích |
| --- | --- | ---: | ---: | --- |
| C-001 | `resolved` | 35.000 | 35.000 | Trễ bốn ngày, approval hợp lệ |
| C-002 | `denied` | 0 | 0 | Order ghi hai ngày trễ; không tin ticket nói năm ngày |
| C-007 | `denied` | 35.000 | 0 | Approval hết hạn; host ghi denial audit |
| C-008 | `resolved` | 35.000 | 20.000 | Approval giới hạn khoản hoàn |
| C-014 | `resolved` | 150.000 | 120.000 | Trừ 30.000 đã hoàn cho cùng đơn |

Nguồn đầu vào/nhãn là `src/data/public_claims.jsonl` và `src/data/public_world_state.json`. Các claim có refund có một audit committed cho claim đang xử lý. C-002 không cần denial audit vì quote bằng 0 và không gọi host ghi refund.

### 4.5. Nghiên cứu và đối chiếu kiến trúc

`src/reports/ablation_orchestrator_vs_swarm.json` ghi nhận orchestrator có pass^5 bằng 1.000, swarm khoảng 0.929 trên cùng bộ public và năm seed. Lỗi quan sát liên quan đến việc tin dữ kiện ticket ở seed 55.

Hai implementation khác nhau về topology, chính sách dùng dữ kiện và số lần gọi model. Vì vậy, kết quả đối chiếu này chưa tách riêng tác động của topology. Diễn giải kết quả cần giữ giới hạn đó; phương pháp và nguồn nghiên cứu xem `report/team/research_card.md`.

## 5. Khó khăn và cách xử lý

- **Python/venv:** máy ban đầu chỉ có Python 3.14 nên lệnh tạo venv bằng Python 3.13 thất bại. Sau khi cài Python 3.13.17, tạo lại venv và xác nhận interpreter trong `src/.venv`, các kiểm tra đã chạy thành công.
- **Lệnh tiếp tục sau lỗi:** PowerShell vẫn thực hiện các dòng sau khi tạo venv thất bại, khiến pip/test chạy bằng Python toàn cục. Cần kiểm tra phiên bản và đường dẫn interpreter trước khi cài dependency/chạy test.
- **Encoding:** dùng `Get-Content -Encoding UTF8` để hiển thị đúng dấu tiếng Việt.
- **Thư mục tạm:** một lần kiểm tra gặp `PermissionError: [WinError 5]` tại fixture setup và cảnh báo cache. Cùng lệnh đã đạt sau khi có quyền truy cập phù hợp, không sửa implementation/test.
- **Lọc test single:** `-k single` khớp cả tên test chung. Khi chỉ kiểm Shape B, dùng `-k "single and not workflow and not orchestrator and not swarm"`; khi kiểm bản tích hợp, chạy toàn bộ matrix.

## 6. Tổng hợp đóng góp

| Thành viên | Phần phụ trách | File/bằng chứng chính |
| --- | --- | --- |
| Nguyễn Công Tĩnh | Workflow, tích hợp, tổng hợp benchmark/crash, ADR và kiểm tra bài nộp | `src/lab8/shapes/workflow.py`, `src/tests/test_workflow_extra.py`, các report chính thức và `report/team/decision_adr.md` |
| Lưu Văn Việt Đức | Single agent, test bổ sung và báo cáo nhóm | `src/lab8/shapes/single.py`, `src/tests/test_single_extra.py`, báo cáo cá nhân và `report/team/group_report.md` |
| Tô Minh Thành | Orchestrator, handoff/trace an toàn, research card và đối chiếu orchestrator–swarm | `src/lab8/shapes/orchestrator.py`, `src/tests/test_orchestrator_handoff.py`, `report/team/research_card.md` và report ablation |

Ba phần triển khai đã tích hợp; kết quả kiểm thử và benchmark được trình bày ở mục 4. Commit đóng góp thực tế được khai báo trong `TEAM.md`; commit phần single và test bổ sung là `dabcf17`. Commit dẫn chứng đánh giá được ghi trong ADR.

ChatGPT, Codex và Claude được sử dụng để hỗ trợ phân tích, triển khai, kiểm thử và biên soạn tài liệu theo phần việc của các thành viên. Chi tiết nằm trong từng báo cáo cá nhân.

## 7. Hạn chế và hướng cải thiện

Kết quả hiện tại gồm kiểm thử public, benchmark 14 claim × 5 seed và crash suite chính thức đạt 20/20. Chưa có kết quả hidden để khẳng định khả năng tổng quát hoặc ngưỡng pass rate hidden.

MockLLM không phải model sản xuất. Workflow và orchestrator hiện điều phối bằng code; chuỗi mô hình không quyết định hành động của single. Draft chưa được dùng làm phản hồi khách hàng. Kết quả policy lookup đầu tiên trong single chưa được sử dụng trực tiếp.

Chi phí được tính theo quy ước mô phỏng, không tính riêng host write, SQL nội bộ và trace I/O. Trace có thể bị ghi đè khi trùng run ID; các lỗi database/filesystem bất thường và cleanup chưa có đầy đủ test riêng. Event count không dùng thay latency.

Lựa chọn workflow phù hợp với dữ liệu có cấu trúc và luật rõ ràng trong lần đo này, không phải kết luận workflow luôn tốt hơn multi-agent. Nếu cần hiểu ticket mơ hồ hoặc điều tra nhiều nguồn độc lập, cần đánh giá lại trên dữ liệu phù hợp. Đối chứng nghiên cứu cần kiểm soát rõ các khác biệt giữa implementation trước khi quy kết nguyên nhân.

## 8. Tài liệu tham khảo

- Yêu cầu: `README.md`, `CHECKPOINTS.md`, `RULES.md`, `RUBRIC.md`, `SUBMISSION.md`, `TEAM.md`.
- [Luật nghiệp vụ](../../docs/business_rules.md), [output/trace contract](../../docs/contracts.md), [kiến trúc](../../docs/architecture.md), [định nghĩa metric](../../docs/metrics.md).
- Code: `src/lab8/shapes/workflow.py`, `single.py`, `orchestrator.py`, `swarm_reference.py`.
- Kiểm thử: `src/tests/test_public_matrix.py` và các test bổ sung của nhóm.
- Dữ liệu/cấu hình: `src/data/public_claims.jsonl`, `src/data/public_world_state.json`, `src/config/`.
- Bằng chứng: `src/reports/benchmark.json`, `src/reports/crash.json`, `src/reports/ablation_orchestrator_vs_swarm.json`.
- [Quyết định kiến trúc](decision_adr.md), [research card](research_card.md), [phụ lục kỹ thuật Shape B](2A202603445_LuuVanVietDuc.md).
