# Memory — 跨對話記憶索引

> 每次對話開始時讀取本檔案。需要更細節時，再讀 `memory/` 內對應分類檔案。

---

## 題目定義（2026-05-12 鎖定，2026-05-14 narrative 收斂至 E）

**Dynamic 2D Rectangle Bin Packing**：把為 static 設計的 2D placement 啟發式（BLF / NFDH / FFDH / Shelf-based）放到有 arrival + departure 的 dynamic 環境下跑，觀察它們的**退化行為與失敗模式**。

- **Framing**：abstract（不綁特定場域；用 Hopper-Turton / Berkey-Wang benchmark + 合成 arrival/departure）
- **Narrative（2026-05-14 收斂）**：**E 變體 — failure mode taxonomy 失敗模式分類學**
  - 一個月內實作 E：跑多 heuristic × 多 workload，命名 + 量化 + 視覺化失敗模式，產出 taxonomy 對照表
  - 5/14 positioning scan 顯示 E 沒有直接 prior art（FPGA 圈僅做 fragmentation metric 不做分類學），差異化空間「強」；A 的軌道被 Burcea 2014 / Wong 2009 競爭分析 + RL baseline 圈搶走，差異化空間「中強」
- **未來延伸（報告結尾要明示）**：E 完成後可 map（對應）到兩條碩論方向
  - **進階 6（Mode 當 RL state feature 模式作為強化學習狀態特徵）**：把 mode label 加進 agent state representation，給 RL 注入 ind  uctive bias
  - **進階 8（Cross-domain transfer 跨領域遷移）**：把 taxonomy 套到 FPGA / Cloud VM / KV-cache 等場域驗證普適性，並作為碩論場域選擇的天然篩選流程
- **報告結尾 bar**（2026-05-12 釐清）：不解決問題，但要立得起 next optimization target——結尾必須能講出「現有方法已優化到 X、我觀察到的 gap 是 Y、下一步可從 6 或 8 切入」
- **Abstract framing 的立論基礎**：不靠 gap 大小，靠**保留選擇權**（場域選擇延至碩論階段，且由進階 8 的驗證流程支撐）

---

## 當前進度

- **研究階段**：Special Topic 題目鎖定 + narrative 收斂至 E（2026-05-14），進入 baseline 實作
- **Special Topic 題目**：Dynamic 2D Rectangle BP + abstract framing（不綁場域）+ **E 變體 failure mode taxonomy**
- **本月目標**：1 個月內實作 E（taxonomy）+ 視覺化原型 + 報告；報告結尾明示往進階 6 / 8 延伸
- **關鍵日期**：6/8 報告週前 8 成完成

## 下次繼續

- **動手前快掃**（已部分完成 2026-05-14）：positioning scan 已產出 A/E 差異化評估與最接近 prior art 清單，**結果摘要見 `memory/literature-map.md` 已掃描清單**；要做的補強：找時間把 Burcea 2014、Wei 2011 IJCAI、Powers 2023 三篇細讀（確認他們確實沒做 taxonomy）
- **第 1–2 週實作**：2D BLF + 合成 arrival/departure baseline（Hopper-Turton benchmark 改造），並準備 ≥ 3 個 heuristic（BLF / NFDH / FFDH / Shelf）共用 placement 介面，方便 E 階段做 heuristic × workload 系統掃描
- **第 3 週**：跨 (heuristic × workload) 掃描，蒐集 bin 狀態時序快照，靠視覺 + 量化 metric 找出反覆出現的失敗形狀
- **第 4 週**：命名 mode → 寫 signature → 寫 mitigation 對照表 → 寫報告（含結尾的進階 6 / 8 future work 段）
- **延後決定**：碩論場域選擇（由進階 8 cross-domain scan 結果支撐）
- **可選**：約楊老師 sanity check Special Topic 方向；將本日轉折寫進 `journal.md`

## 重要提醒

- 重思考／一次性內容（debugging、code review、scratch analysis）用英文以節省 token，最終產出用中文
- 本專案 memory 系統與 harness 自動 memory（`~/.claude/projects/.../memory/`）並存、互不干擾
- 寫入記憶時：在對應分類檔案最上方新增 `## YYYY-MM-DD` 段落，最新日期置頂
- 對未拍板的方向，記錄時要區分「已釐清的理解」vs「尚待決定的選項」，不要寫成已決定
- **場域選擇延後**：Special Topic 階段刻意不綁特定 home application；FPGA 只當文獻背景知識，不當研究場域
- **碩論貢獻評估**先不套用於 Special Topic 選題——會癱瘓選題決策

---

## 索引

- [research-decisions.md](memory/research-decisions.md) — 研究方向決策、放棄的方向、選題理由
- [progress.md](memory/progress.md) — 階段性進展、里程碑、卡關狀況
- [ideas.md](memory/ideas.md) — 研究點子、跨領域聯想、零散發想
- [candidate-topics.md](memory/candidate-topics.md) — Bin-Packing 候選題目完整分析（篩選判準、軸組合、視覺揭露力）
- [literature-map.md](memory/literature-map.md) — 文獻掃描中心檔案：方法家族、關鍵字、必讀 survey、第一輪查詢、操作指引（H1–H5 假設驅動）
- [experiments.md](memory/experiments.md) — 實作過程、踩過的雷、baseline 結果、資料來源
