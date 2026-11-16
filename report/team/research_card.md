# Research card

File này nằm cố định ở `report/team/research_card.md`; `python -m lab8.check_submission` đọc cột "Nhóm điền" bằng máy.

Phần này nối tiếp phần mini research ở buổi lý thuyết (slide 62–63). Chọn **một** câu R1–R4, điền 6 dòng, rồi biến nó thành **một ablation** chạy được trong lab: giữ nguyên model (MockLLM), tool, seed, corpus và giá, chỉ thay đổi một biến.

| Câu | Nguồn (thư viện tham khảo, slide 68–69) | Câu hỏi gợi ý cho lab |
| --- | --- | --- |
| R1 · Scaling | Google Research 2026, *Towards a Science of Scaling Agent Systems* | Task claims chủ yếu tuần tự hay song song được? Dự đoán thêm investigator sẽ làm pass rate và cost/success thay đổi thế nào. |
| R2 · Failure taxonomy | MAST, NeurIPS 2025, *Why Do Multi-Agent LLM Systems Fail?* | Các trial fail của swarm (seed 55) thuộc nhóm nào: lỗi giao việc, lệch mục tiêu, hay lỗi kiểm chứng? |
| R3 · Architecture choices | AgentArch, AACL 2026 | Nếu đổi topology mà giữ nguyên mọi thứ khác, biến nào phải cố định để kết luận còn đúng? |
| R4 · Evaluation confounders | EMNLP 2026, *Rethinking Evaluation of MAS Efficiency* | Làm sao chứng minh chênh lệch giữa A/B/C/D là do topology, không phải do prompt, tool hay seed? |

## Phiếu của nhóm

Điền vào cột cuối. Không xóa hai cột đầu.

| Field | Hướng dẫn | Nhóm điền |
| --- | --- | --- |
| CÂU | R1 / R2 / R3 / R4 | R2 |
| SOURCE | Paper/blog, năm, URL, loại bằng chứng (benchmark, production report, blog kinh nghiệm) | MAST, NeurIPS 2025, *Why Do Multi-Agent LLM Systems Fail?* — benchmark trên nhiều hệ thống MAS |
| CLAIM | Một kết luận gốc của nguồn. Không viết rộng hơn phạm vi paper | Các lỗi trong hệ MAS thường thuộc một trong ba nhóm: lỗi giao việc (task delegation), lệch mục tiêu (goal misalignment), hoặc lỗi kiểm chứng (verification failure) |
| BOUNDARY | Model / dataset / setup giới hạn kết luận đó | Nghiên cứu trên các MAS sử dụng LLM thực; không áp dụng trực tiếp cho MockLLM. Swarm reference dùng seed % 5 == 0 để tạo lỗi có kiểm soát |
| HYPOTHESIS | Nếu đổi shape A→B (hoặc bật/tắt một thành phần), metric X sẽ đổi theo hướng nào, khoảng bao nhiêu | Nếu đổi swarm (có weakness) → orchestrator (không trust ticket delay), pass^5 sẽ tăng từ 0.929 lên 1.000 vì loại bỏ lỗi kiểm chứng (seed-based model override) |
| METHOD | Biến giữ cố định: model, tools, seed, corpus, giá, evaluator. Biến duy nhất được thay đổi: … | Giữ cố định: MockLLM, tools (lookup_order/policy/compute_compensation), seeds (11,22,33,44,55), corpus (public_claims.jsonl), giá (pricing.yaml), evaluator (trial_pass). Biến thay đổi duy nhất: topology shape (swarm → orchestrator) |
| FAILURE / METRIC | Một lỗi dự kiến và cách đo nó: pass rate, pass^5, variance, cost/success, leak, bypass | Lỗi dự kiến: swarm tin ticket delay thay vì DB trên seed % 5 == 0 (C-002, seed=55 → "resolved" thay vì "denied"). Đo bằng pass^5 (tất cả 5 seed phải pass để trial claim pass) và seed_variance |

## Kết quả ablation

- Lệnh đã chạy (copy nguyên văn):
  ```
  python -m lab8.benchmark --shapes orchestrator,swarm --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/ablation_orchestrator_vs_swarm.json
  ```
- Run id / file report: `reports/ablation_orchestrator_vs_swarm.json`
- Kết quả so với hypothesis (đúng / sai / không kết luận được), kèm số liệu:
  - **Đúng**: orchestrator đạt pass^5 = 1.000, swarm đạt pass^5 = 0.929, seed_variance swarm = 0.000816 (orchestrator = 0.000000)
  - Lỗi dự kiến xảy ra đúng: swarm trả "resolved" thay vì "denied" trên C-002 seed=55 (1 trial fail)
  - Orchestrator không có weakness này → pass rate 1.000 trên mọi seed
- Giới hạn: MockLLM không phải model sản xuất, latency là `unavailable`.

Muốn đi xa hơn một ablation để lấy điểm cộng thì xem [docs/bonus_topics.md](../../docs/bonus_topics.md).
