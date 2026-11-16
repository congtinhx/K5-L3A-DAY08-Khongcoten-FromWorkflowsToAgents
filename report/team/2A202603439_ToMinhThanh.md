# Báo cáo cá nhân — 2A202603439_ToMinhThanh

## 1. Thông tin thành viên

- Họ tên: Tô Minh Thành
- MSSV: 2A202603439
- Email: tominhthanh75@gmail.com
- GitHub: thanh211124

## 2. Phần việc phụ trách

- Shape C `orchestrator` (`src/lab8/shapes/orchestrator.py`): orchestrator điều phối investigator đọc dữ liệu, sau đó orchestrator gọi `issue_refund`. Handoff chỉ cấp read-only tools; trace không ghi raw claim row hay order row (không lộ secret, SĐT, địa chỉ).
- Test file `src/tests/test_orchestrator_handoff.py`: kiểm tra trace/handoff không chứa `CANARY_SECRET_` hay `parent_secret`, investigator không có write tool, trace luôn được ghi kể cả trên early-return path.
- Phiếu nghiên cứu `report/team/research_card.md` (câu R2 — MAST NeurIPS 2025) + ablation orchestrator vs swarm.

## 3. Đóng góp cụ thể

- Viết `src/lab8/shapes/orchestrator.py`:
  - Dùng `make_handoff` với `allowed_tools=["lookup_order", "lookup_policy", "compute_compensation"]` (read-only).
  - Trace ghi handoff đã sanitize (qua `safe_dump`), không ghi row gốc từ DB.
  - Orchestrator gọi `issue_refund` sau khi investigator xong; không để investigator gọi write tool.
  - Truyền `crash_at` vào `issue_refund`, không bắt `InjectedCrash`.
  - Mọi nhánh return đều qua `finish()` để trace luôn được ghi.
- Viết `src/tests/test_orchestrator_handoff.py` (9 tests):
  - `test_trace_no_canary_secret`, `test_trace_no_canary_secret_all_claims`: trace không chứa secret.
  - `test_handoff_no_write_tools`, `test_investigator_cannot_call_write_tool`, `test_investigator_cannot_call_append_audit`: investigator bị chặn write.
  - `test_trace_has_run_id_and_events`: trace contract v1.
  - `test_early_return_needs_info_still_has_trace`, `test_escalated_no_refund_no_secret`: early-return vẫn có trace sạch.
  - `test_handoff_sanitize_drops_parent_secret`: sanitize xóa secret trước khi ghi trace.
- Điền `report/team/research_card.md` (R2) và chạy ablation.

## 4. Bằng chứng

- 9/9 tests trong `test_orchestrator_handoff.py` pass.
- Student matrix tests: 62/62 passed (`pytest -q -m student -o addopts= -k orchestrator`).
- Ablation run: `reports/ablation_orchestrator_vs_swarm.json`
  - orchestrator: pass_rate=1.000, pass^5=1.000, variance=0.000000
  - swarm: pass_rate=0.986, pass^5=0.929, variance=0.000816 (C-002 seed=55 fail như dự đoán)

## 5. Công cụ AI đã dùng

Dùng Claude (Kiro/Claude Code) để hỗ trợ viết code. Tự kiểm tra bằng cách:
- Chạy toàn bộ test suite để xác nhận không break test có sẵn.
- Chạy student matrix tests (62 cases) trực tiếp để xác nhận logic đúng.
- Đọc từng file tham chiếu (`swarm_reference.py`, `handoff.py`, `runtime.py`) để hiểu contract trước khi viết.

## 6. Tự đánh giá

Phần orchestrator đã đáp ứng các yêu cầu: handoff chỉ có read-only tools, trace không lộ secret, investigator bị chặn write, `crash_at` được truyền đúng, mọi early-return đều có trace. Ablation xác nhận hypothesis R2: loại bỏ weakness "trust ticket delay" (swarm → orchestrator) làm pass^5 tăng từ 0.929 lên 1.000.
