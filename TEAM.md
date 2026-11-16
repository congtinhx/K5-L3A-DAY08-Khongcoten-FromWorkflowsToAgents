# Team

## Thông tin nhóm

- Tên nhóm: Khongcoten
- Lớp: L3A
- Repo nhóm: `K5-L3A-DAY08-Khongcoten-FromWorkflowsToAgents` (xem [SUBMISSION.md](SUBMISSION.md))
- URL repo, nhánh nộp, commit chốt: https://github.com/congtinhx/K5-L3A-DAY08-Khongcoten-FromWorkflowsToAgents, nhánh `main`, commit chốt (benchmark/crash): `6d6c877`

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
|   1 | Nguyễn Công Tĩnh | 2A202603373 | tinh22102004@gmail.com | congtinhx | Nhóm trưởng; Shape A workflow + integration (repo, benchmark, crash suite, ADR, check_submission) |
|   2 | Lưu Văn Việt Đức | 2A202603445 | luuvanvietduc@gmail.com | VietDuc | Shape B single (ReAct) + báo cáo nhóm |
|   3 | Tô Minh Thành | 2A202603439 | tominhthanh75@gmail.com | thanh211124 | Shape C orchestrator + handoff/trace an toàn + research card |

Gợi ý chia vai:

- Nhóm 6 người: integration; workflow; single agent; orchestrator; ledger/policy/crash; eval/report.
- Nhóm 4 người: workflow + integration; single; orchestrator + handoff; ledger + evaluation.

## Bảng đóng góp

`python -m lab8.check_submission` đọc bảng này bằng máy: giữ nguyên tiêu đề `## Bảng đóng góp` và các cột. Mỗi người một dòng: commit có nội dung và ít nhất một test đã thêm hoặc sửa.

| Người | Vai | Commit | Test đã thêm hoặc sửa |
| --- | --- | --- | --- |
| Nguyễn Công Tĩnh (2A202603373) | Workflow + integration | `e374fd9`, `70fc37e`, `6d6c877` | `src/tests/test_workflow_extra.py` |
| Lưu Văn Việt Đức (2A202603445) | Single (ReAct) + báo cáo nhóm | `dabcf17` | `src/tests/test_single_extra.py` |
| Tô Minh Thành (2A202603439) | Orchestrator + handoff + research card | `b4d886c`, `49cf394` | `src/tests/test_orchestrator_handoff.py` |

## Cá nhân

Mỗi thành viên đồng thời tạo một báo cáo riêng trong `report/` theo dạng:

```text
report/team/MSSV_HoTen.md
```

Ví dụ: `report/team/20241234_NguyenVanAn.md`.

File báo cáo cá nhân của nhóm:

- `report/team/2A202603373_NguyenCongTinh.md`
- `report/team/2A202603445_LuuVanVietDuc.md`
- `report/team/2A202603439_ToMinhThanh.md`

## 2A202603373_NguyenCongTinh

### Phần việc phụ trách

- Shape A `workflow` (`src/lab8/shapes/workflow.py`)
- Integration: tạo repo nhóm, merge nhánh, chạy `reports/benchmark.json` và `reports/crash.json`, điền `report/team/decision_adr.md`, chạy `check_submission`, nộp bài

### Đóng góp cụ thể

- `e374fd9` feat(workflow): viết Shape A `workflow` theo 8 bước — đọc claim qua `get_claim_view`, tra đơn qua `lookup_order` (allowlist), tính tiền bằng `compute_compensation` từ dòng order, gọi `durability.issue_refund` với quote đầy đủ và `crash_at`; không đọc số ngày trễ trong ticket, không gọi model
- `70fc37e` test(workflow): `src/tests/test_workflow_extra.py` (C-002 seed 55 vẫn `denied`, C-009 "ignore policy" không tạo refund)
- Integration: tạo repo nhóm, gộp 3 nhánh vào `main`, `6d6c877` sinh `src/reports/benchmark.json` và `src/reports/crash.json`, viết `report/team/decision_adr.md` (chọn workflow)

### Bằng chứng

- `python -m pytest -q -m student -o addopts= -k workflow`: 62 passed; sau khi gộp: `python -m pytest -q` xanh, bộ student 248 passed
- `src/reports/crash.json`: 20/20
- `src/reports/benchmark.json`: workflow pass 1.000, pass^5 1.000, variance 0, cost/success 27.86 VND mô phỏng (thấp nhất 4 shape)
- Run id: `R-workflow-C-002-s55`, `R-workflow-C-009-s55`
- Báo cáo cá nhân: `report/team/2A202603373_NguyenCongTinh.md`

## 2A202603445_LuuVanVietDuc

### Phần việc phụ trách

- Shape B `single` (`src/lab8/shapes/single.py`)
- Báo cáo nhóm `report/team/group_report.md`

### Đóng góp cụ thể

- `dabcf17`: viết Shape B `single` (vòng ReAct `run_react`, tối đa 8 bước, model chỉ chọn tool đọc, code gọi `issue_refund` sau vòng lặp)
- Test `src/tests/test_single_extra.py`
- Báo cáo nhóm `report/team/group_report.md`

### Bằng chứng

- `python -m pytest -q -m student -o addopts= -k single`: 62 trial ma trận public của single pass
- Test: `test_single_rejected_write_returns_failure_with_trace`, `test_single_step_cap_returns_failure_with_trace`, `test_single_ticket_injection_cannot_change_order_facts`, `test_single_all_crash_windows_resume_once`
- `src/reports/benchmark.json`: single pass 1.000, pass^5 1.000, cost/success 39.19 VND mô phỏng
- Báo cáo cá nhân: `report/team/2A202603445_LuuVanVietDuc.md`

## 2A202603439_ToMinhThanh

### Phần việc phụ trách

- Shape C `orchestrator` (`src/lab8/shapes/orchestrator.py`), handoff allowlist và trace an toàn
- Phiếu nghiên cứu và ablation `report/team/research_card.md`

### Đóng góp cụ thể

- `b4d886c` feat(orchestrator): viết Shape C `orchestrator` — handoff tạo bằng `make_handoff` chỉ cấp tool đọc, chạy `run_readonly_investigators`, orchestrator mới gọi `issue_refund`; trace chỉ ghi handoff đã sanitize
- Test `src/tests/test_orchestrator_handoff.py`
- `49cf394`: ablation orchestrator vs swarm cho research card (câu R2)

### Bằng chứng

- `python -m pytest -q -m student -o addopts= -k orchestrator`: 62 passed
- Test: `test_trace_no_canary_secret_all_claims`, `test_handoff_no_write_tools`, `test_investigator_cannot_call_write_tool`, `test_handoff_sanitize_drops_parent_secret`
- Ablation: `python -m lab8.benchmark --shapes orchestrator,swarm --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/ablation_orchestrator_vs_swarm.json`
- `src/reports/benchmark.json`: orchestrator pass 1.000, pass^5 1.000, cost/success 46.43 VND mô phỏng
- Báo cáo cá nhân: `report/team/2A202603439_ToMinhThanh.md`, `report/team/research_card.md`
