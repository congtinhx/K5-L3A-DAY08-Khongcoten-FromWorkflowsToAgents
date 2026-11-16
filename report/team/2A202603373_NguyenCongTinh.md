# Báo cáo cá nhân — 2A202603373_NguyenCongTinh

## 1. Thông tin thành viên

- Họ tên: Nguyễn Công Tĩnh
- MSSV: 2A202603373
- Email: tinh22102004@gmail.com
- GitHub: congtinhx

## 2. Phần việc phụ trách

- Nhóm trưởng, integration: tạo repo nhóm, mời thành viên, gộp 3 nhánh vào `main`, chạy cổng host và bộ student.
- Shape A `workflow` (`src/lab8/shapes/workflow.py`).
- Test `src/tests/test_workflow_extra.py`.
- Sinh `src/reports/benchmark.json`, `src/reports/crash.json`; viết `report/team/decision_adr.md`; chạy `check_submission` và nộp bài.

## 3. Đóng góp cụ thể

- Commit `e374fd9` — feat(workflow): shape A deterministic workflow. Đọc claim qua `get_claim_view`, tra đơn qua `lookup_order` (allowlist field), tính tiền bằng `compute_compensation` từ dòng order trong DB, gọi `durability.issue_refund` với quote đầy đủ và `crash_at`.
- Commit `70fc37e` — test(workflow): 3 test cho C-002 seed 55 và C-009.
- Quyết định kỹ thuật:
  - Không đọc ticket để lấy số ngày trễ, nên C-002 seed 55 vẫn `denied` (đúng chỗ swarm sai).
  - Không gọi MockLLM: docstring cho phép, giúp cost/success thấp nhất và kết quả không phụ thuộc seed.
  - Khi `InjectedCrash`: ghi trace rồi ném lại, không nuốt lỗi; các lỗi khác trả `failed` để `run_claim` không ném exception.
  - Trace chỉ ghi `claim_id`, cờ `has_order_id`, order view đã allowlist, quote, kết quả host, quyết định cuối. Không ghi ticket, `principal_id`, secret, PII.
  - Chọn workflow trong ADR vì cùng pass rate 1.000 với single và orchestrator nhưng cost/success thấp nhất (27.86 VND mô phỏng).

## 4. Bằng chứng

- `python -m pytest -q -m student -o addopts= -k workflow`: 62 passed.
- Sau khi gộp 3 nhánh: `python -m pytest -q` xanh; bộ student 248 passed.
- `python -m lab8.crash_test --count 20 --out reports/crash.json`: crash_safety 20/20.
- `src/reports/benchmark.json`: workflow pass 1.000, pass^5 1.000, variance 0, cost/success 27.86, mean steps 4.43.
- Run id: `R-workflow-C-002-s55` (denied, không refund), `R-workflow-C-009-s55` (denied, không refund).
- Test: `test_c002_seed55_still_denied_ignores_ticket_delay`, `test_c002_same_result_on_every_seed`, `test_c009_ignore_policy_creates_no_refund`.

## 5. Công cụ AI đã dùng

- Claude: hướng dẫn cài đặt, gợi ý code `workflow.py` và `test_workflow_extra.py` theo docstring và `docs/contracts.md`, soạn nháp ADR và báo cáo này.
- Tự kiểm tra: tự chạy smoke, cổng host, bộ student `-k workflow`, crash test và benchmark trên máy; đối chiếu từng bước code với 8 bước trong docstring và bảng luật ở `docs/business_rules.md`; đọc lại số liệu ADR từ `src/reports/benchmark.json`.

## 6. Tự đánh giá

Hoàn thành shape workflow, test bổ sung, tích hợp, benchmark, crash suite và ADR đúng hạn. Shape đạt toàn bộ ma trận public trên 5 seed và crash 20/20. Hạn chế: chưa kiểm được trên bộ hidden 40 claim; số liệu cost là mô phỏng.