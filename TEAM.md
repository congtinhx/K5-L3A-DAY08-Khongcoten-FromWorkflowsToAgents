# Team

## Thông tin nhóm

- Tên nhóm: Khongcoten
- Lớp: L3A
- Repo nhóm: `K5-L3A-DAY08-Khongcoten-FromWorkflowsToAgents` (xem [SUBMISSION.md](SUBMISSION.md))
- URL repo, nhánh nộp, commit chốt:

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
| Nguyễn Công Tĩnh (2A202603373) | Workflow + integration | | `src/tests/test_workflow_extra.py` |
| Lưu Văn Việt Đức (2A202603445) | Single (ReAct) + báo cáo nhóm | | `src/tests/test_single_extra.py` |
| Tô Minh Thành (2A202603439) | Orchestrator + handoff + research card | | `src/tests/test_orchestrator_handoff.py` |

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

-

### Bằng chứng

-

## 2A202603445_LuuVanVietDuc

### Phần việc phụ trách

- Shape B `single` (`src/lab8/shapes/single.py`)
- Báo cáo nhóm `report/team/group_report.md`

### Đóng góp cụ thể

-

### Bằng chứng

-

## 2A202603439_ToMinhThanh

### Phần việc phụ trách

- Shape C `orchestrator` (`src/lab8/shapes/orchestrator.py`), handoff allowlist và trace an toàn
- Phiếu nghiên cứu và ablation `report/team/research_card.md`

### Đóng góp cụ thể

-

### Bằng chứng

-
