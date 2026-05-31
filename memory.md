# Memory — 跨對話記憶索引

> 對話啟動必讀。**只放指標、穩定狀態、下次繼續**；資料／表格／時序紀錄一律在 detail 檔。寫入規則見 `CLAUDE.md` 的 memory_protocol。

---

## 題目定義（鎖定 2026-05-12 / narrative 收斂 2026-05-14）

**Dynamic 2D Rectangle Bin Packing** — observe BLF/NFS/FFS/BFS heuristic 在 dynamic（arrival+departure）下的退化／失敗模式。

- **Framing**：abstract（不綁場域），Hopper-Turton + 合成 workload
- **Narrative**：**E 變體** — failure mode taxonomy（命名 + 量化 + 視覺化）
- **報告 bar**：不解問題，但結尾要立得起 next optimization target → 進階 6 (Mode-as-RL-feature) 或 8 (Cross-domain transfer)
- **背景／rationale**：→ research-decisions 2026-05-12、2026-05-14

---

## 下次繼續（接續時讀這段）

老師 meeting 完成（2026-05-25）。主軸確認：根據 bin 狀態動態選最佳 heuristic。但 **Oracle Gap = 0%**（BLF 全勝 150/150 runs），現有 heuristic 集合無法支撐 dynamic switching。→ exp 2026-05-25、decisions 2026-05-25

**優先順序（調整後）**：

1. **prior work 細讀**：Burcea 2014 / Wei 2011 / Powers 2023（原目標：避開重命名）+ **新目標：找 dynamic heuristic switching 相關研究 + 查 DRL 論文的衡量指標與比較對象**（老師問的）
   - 〔2026-05-30 部分完成〕已掃出「依狀態選 heuristic」= selection HH（Özcan-Parkes-Asta）+ RL-for-BP 成熟範式 → 核心 idea 非新，novelty 須靠 2D+departure+可解釋 mapping+視覺化的組合（→ literature-map / ideas 2026-05-30）。**仍欠**：(a) 窮盡確認 2022–2025 有無「2D DBP with departure + RL/HH 動態選法」（novelty 存亡）；(b) DRL 論文衡量指標 + 比較對象的逐篇整理。
2. **擴充 heuristic 集合**：加入幾何式方法（Maxrects / Skyline / Guillotine），讓不同 heuristic 在不同 mode 下互有勝負。→ ideas 2026-05-25
3. **重算 Oracle Gap**：擴充後重跑，確認 Gap > 0 → dynamic switching 有價值
4. **命名 mode + 報告**：6 個 mode 已存活（≥ 60% 門檻），待 #1 完成後正式命名

**不變的狀態指標**：signature 2D（peak PE + discard）為主、mean/peak 為輔；PCA 92% 變異在 2D；FFS ≡ BFS；light_dep ≡ heavy_dep 在 peak signature 上無法分離。


---

## 重要提醒

- **Oracle Gap = 0%**（BLF 全勝）→ 現有 4 heuristic 不支撐 dynamic switching；擴充幾何式 heuristic 是前提條件
- **Per-timestep oracle ≥ per-workload oracle**（嚴格超集）→ per-workload = 0 不蘊含 per-timestep = 0；實作前必須先拍板 3 個設計選擇（lookahead 範圍 / switching cost / beam vs greedy）→ decisions 2026-05-30
- 場域選擇延後到碩論階段，Special Topic 不綁特定 application
- 碩論貢獻評估**不**套用於 Special Topic 選題（會癱瘓）
- 重思考用 English 省 token，最終產出用中文
- 程式指令一律在 `code/` 內：`uv run pytest` / `uv run python scripts/demo_grid_view.py`
- 對未拍板方向，區分「已釐清」vs「待決定」，不要寫成已決定
- 候選 mode 名字是**假設**，不是 prior work 結論；E 的貢獻就是把這些變成證據

---

## 索引

- [research-decisions.md](memory/research-decisions.md) — 研究方向／實驗設定／方法論決策（**為什麼選 X**）
- [experiments.md](memory/experiments.md) — 跑了什麼、得到什麼（資料、表格、踩雷）
- [progress.md](memory/progress.md) — 里程碑、卡關狀況、週時程實況
- [ideas.md](memory/ideas.md) — 未來延伸方向、跨領域聯想
- [candidate-topics.md](memory/candidate-topics.md) — 候選題目完整分析（archive 性質）
- [literature-map.md](memory/literature-map.md) — 文獻掃描中心、survey 入口、H1–H5 操作指引
- [inbox.md](memory/inbox.md) — 不確定分類的暫存，consolidation 時 drain
