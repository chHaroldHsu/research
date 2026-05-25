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

前置 #2–#5 **全部完成**（2026-05-23，30 seeds × 600 runs）。剩下 **#1 prior work** 即可開始命名 mode。最新分析 → experiments 2026-05-23。

**A. 剩餘前置**

1. **prior work 細讀**（命名 mode 前必須）：Burcea 2014 / Wei 2011 IJCAI / Powers 2023——避開重命名 + 釐清貢獻邊界（dynamic-only mode 是哪些）

**B. 命名 mode 起手**

2. **命名 mode**：6 個量化 mode 已存活（≥ 60% 門檻），套統一命名規則
   - Heuristic-intrinsic（baseline）：Brick-wall、Horizontal-stripe
   - Workload-induced（貢獻）：Top-sliver、Sparse-BLF、Item-too-tall、Sparse-stripe
   - **退場**：Inland Island（signature 重疊 d/σ=0.16，視覺無區別）、Shelf abandonment（NFS 與 FFS/BFS 同 mode 標籤）
3. **寫 mode signature**：每 mode 一組 (peak PE, discard, mean/peak) + 視覺特徵 + 30-seed 穩定比例。F@peak 已從 signature 完全降級
4. **Mitigation 對照表**：每 mode 對哪個 heuristic 怎麼緩解（猜想可標 [假設]）
5. **跑 Oracle Gap**：X = single-best heuristic 平均 PE / Y = mode-aware oracle 平均 PE / Gap = Y - X → 報告 punchline + 進階 6 target。GT 三層架構見 decisions 2026-05-22
6. **報告 8 成完成**：含進階 6 (RL-feature) / 8 (cross-domain) future work 段

**狀態指標**：signature 改為 **2D（peak PE + discard）為主、mean/peak 為輔**（F@peak 完全降級）；PCA 確認 92% 變異在 2D；7 個視覺 cluster 清楚分群。新發現：**light_dep ≡ heavy_dep 在 peak signature 上無法分離**（d/σ ≤ 0.16，跨所有 heuristic）→ 時序維度才能區分。FFS ≡ BFS 在 4 個 metric 全部成立。最新數據 → experiments 2026-05-23。


---

## 重要提醒

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
