# 研究決策

> 紀錄研究方向的關鍵決策、放棄的方向、選題理由。
> 格式：`## YYYY-MM-DD` 為段落標題，最新日期置頂。

---

## 2026-05-18

### Heuristic 集從 {BLF, NFDH, FFDH, Shelf} 改為 {BLF, NFS, FFS, BFS}

**動機**：NFDH / FFDH 名字裡的 "DH"（Decreasing Height）需要先把所有 item 按高度遞減排序，這是**offline** 假設——在 dynamic online + departure 設定下做不到（不知道未來 item）。本研究刻意鎖 online（item 一個個來、來了就要放、不能 buffer），所以 textbook NFDH/FFDH 不適用。

**新集合（皆 online shelf 家族）**：
- **NFS**（Next-Fit Shelf）：只看當前最近開啟的 shelf；不夠就開新的
- **FFS**（First-Fit Shelf）：依開啟順序掃所有 shelf，第一個塞得下就用
- **BFS**（Best-Fit Shelf）：所有能放的 shelf 中選「剩餘高度最小」者

**Shelf 語意（textbook 純粹版）**：x-cursor **只前進不回退**——shelf 內 item departure 留下的 cell 不可重用。這正是要觀察的失敗模式（候選 "Departed-item Ghost" / Top-Shelf Waste），不是 bug。

**未取 NFDH/FFDH 作 offline upper bound 對照**：實作 + 解讀成本上升；narrative 也會被「online vs offline 差距」分散注意力。若第 3 週發現需要量化「online 損失多少」，再考慮加。

**為何 4 個夠不另加 Skyline**：BLF 已是無 shelf 結構的代表，BFS 與 FFS 形成「best vs first」對照組，4 個已涵蓋「無結構 / 順序開啟 / 緊湊匹配」三軸。Skyline 與 BLF 重疊度高，先省下。

---

## 2026-05-14

### Narrative 收斂：選 E 變體（failure mode taxonomy 失敗模式分類學）

原計畫 5/31 看實作結果再決定 A vs E，本日提前收斂至 E。觸發點：今日做了快速 positioning scan（agent 驅動，~30 分鐘），結果顯示兩條路線的 prior art 密度差距明確。

**Scan 結果摘要**（細節見 `memory/literature-map.md` 已掃描清單）：
- A（heuristic 排名重洗）：理論側被 Burcea 2014 / Wong 2009 占走（competitive ratio 競爭比分析），實證側 RL 圈（Deep-Pack 2019、arXiv 2409.09677 2024）用 BLF/Shelf 當 baseline 但全部 no-departure（無離開）。差異化「中強」
- E（failure mode taxonomy）：FPGA 圈 Tabero 2006 / Wei 2011 / Powers 2023 都做 fragmentation metric（碎片度量）或 defrag heuristic（重整啟發式），**沒人做命名 + 量化 + 視覺化的分類學**。差異化「強」

**E 的 so what 鏈條**（解釋為何接受 E 的天花板更高 / 地板更低）：
- 表面貢獻：命名 dynamic-only 失敗模式，給後續研究 attack target（攻擊目標）選單
- E 立得起的四條件：(1) Distinct mechanism 不同機制；(2) Quantitative signature 量化簽章；(3) Actionable mitigation 可操作緩解；(4) Systematic observation 系統觀察
- E 失敗回退路徑：若找不到 ≥ 3 個 distinct mode，退回 A 的 ranking-inversion（排名反轉）報告

**未來延伸路徑（報告結尾明示）**：E 完成後可 map 到兩條碩論方向（見 `memory/ideas.md` 2026-05-14 段細節）
- 進階 6：Mode 當 RL state feature（模式作為強化學習狀態特徵）
- 進階 8：Cross-domain transfer（跨領域遷移）—— 同時是碩論場域選擇的天然篩選流程

**為何不提前 commit A**：A 的 so what 弱在「現象觀察沒解釋」；要立得起必須做歸因，而歸因會自然滑向 E

### 一個月實作 schedule

- 第 1–2 週：BLF baseline + 合成 arrival/departure workload generator，且共用 placement 介面以便接 NFS/FFS/BFS（見 2026-05-18 段，原 NFDH/FFDH 改為 online shelf 家族）
- 第 3 週：跨 (heuristic × workload) 系統掃描，採集 bin 狀態時序快照
- 第 4 週：命名 mode + signature + mitigation 對照表 → 報告 8 成完成（含進階 6 / 8 future work 段）

### 既有 5/31 決策節點作廢，但保留以下檢核

- 第 3 週末若找不到 ≥ 3 個 distinct mode → 觸發退回 A 的決定點
- 若 baseline 跑不通 → 觸發題目層級重議（不太可能但保留 safety net）

### 方法論釐清：候選 mode 名字是假設，不是已驗證結論

「Sliver Strip 細條夾縫 / Inland Island 內陸孤島 / Boundary Lockout 邊界鎖死 / Staircase Skyline 階梯天際線」這 4 個名字是對話中提出的 **starting hypothesis（起始假設）**，**不是 prior work 已驗證的結論**。其知識基礎強度：
- **強**：dynamic 2D BP 會 fragment（Tabero 2006 / Powers 2023 / Wei 2011 實證過）
- **中**：洞形狀隨 heuristic / workload 變化（FPGA 文獻零散觀察，未系統化）
- **猜**：具體 4 個 mode 名字 + signature 邊界條件 + 「Sliver 對應 BLF」這類 mapping

**E 的 contribution（貢獻）正是「透過實驗把這些假設變成證據」**——若 mode 名字早已有人寫好，E 就不是新貢獻。預設的 4 個 mode 是討論用的 scaffold（腳手架），不是結論。

### 實驗設計：必須是 factorial（因子）設計 H × W

**問題意識**：「不管哪個 heuristic 都會留洞，洞形狀取決於進出時間」——單看一個 heuristic 不能歸因，會被 workload 當 confounding variable（混淆變數）。

**解法**：第 3 週掃描**必須是 H × W 網格**：
- H = {BLF, NFS, FFS, BFS}（4 個 heuristic，皆為 online；見 2026-05-18 段）
- W = {至少 3–5 個 workload，覆蓋 light/heavy departure、不同 size distribution 大小分布、不同 lifetime distribution 壽命分布}
- 每格紀錄 PE（裝填效率）+ bin 狀態時序快照 + 出現的 mode

**訊號分解（attribution analysis 歸因分析）**：
- **行向**（固定 workload 掃 heuristic）：heuristic 是否主導 mode 形狀
- **列向**（固定 heuristic 掃 workload）：workload 是否主導 mode 形狀
- **交互作用 (interaction)**：mode 是否只在特定 (heuristic, workload) 組合下出現

### 4 種可能結果 × E 的成立條件

| 結果情境 | 解讀 | E 還成立嗎？ |
|---|---|---|
| (1) Heuristic 主導 — 同 workload 下不同 heuristic 產出不同 mode | E 原始 framing 成立 | ✅ |
| (2) Workload 主導 — 所有 heuristic 在同 workload 下產相同 mode | Taxonomy 改框為「**workload-induced mode**」，仍是新貢獻（prior work 沒做此 mapping） | ✅（reframe） |
| (3) Interaction 主導 — mode 只在特定 (H, W) 組合下出現 | E 升級為 (heuristic, workload) → mode 對應表，貢獻最大 | ✅（最強） |
| (4) 無 distinct mode — 洞形狀全部糊在一起無法分類 | Taxonomy 不存在 | ❌ 觸發退回 A |

**重要**：safety net 的觸發條件是「找不到 ≥ 3 個 distinct mode」，**不是**「找不到 ≥ 3 個 heuristic-specific mode」——情境 (2) 不觸發退路。

### 對 prior work 的差異化補強

H × W 因子設計本身就是 prior work 沒做的：Tabero / Powers 只看 aggregate metric（聚合指標），沒做這個歸因拆解。這層方法論補在 `memory/literature-map.md` 變體 E 差異化矩陣的「跨 heuristic × workload 系統掃描」維度。

---

## 2026-05-12

### 收斂結論（同日下午）

**Special Topic 鎖定**：候選 A（Dynamic 2D Rectangle BP）+ **abstract framing**（用 Hopper-Turton / Berkey-Wang benchmark + 合成 arrival/departure，不綁特定場域）。程式碼路線優先實作；narrative（A 原版 vs E 變體 Failure Mode Taxonomy）延至 5/31 前再決定——前 3 週實作共用，第 4 週看結果再選

**場域框架延後**：Special Topic 階段刻意不投入特定場域 system knowledge；場域選擇（GPU / Cloud / KV-cache / 其他）留待碩論階段，依產學連結或興趣
- Why：場域是一次性難回頭的決定，學習投資沉重；Special Topic 階段以「generic dynamic 2D BP 退化行為觀察」為主張，場域變 future work

**FPGA 地位釐清**：歷史上文獻最厚的 Dynamic 2D Rect BP 場域，但 gap 小（30 年累積 + 2020 後領域退潮）。**只當文獻背景知識，不當研究場域**

**選題判斷的 5 角度框架**（純 Special Topic 標準，碩論貢獻先不算）：
1. Baseline 可實作性（1–2 週端到端跑通；演算法、資料、metric 明確）
2. 問題定義鋒利度（input/output/objective、與經典 BP 的 delta、為什麼難都講得清）
3. 報告呈現力（一個月後能講「做了 X、觀察 Y、下一步 Z」；結果可量化）
4. 風險可控性（fallback 路徑、前置學習 <5 篇硬核論文、工具鏈現成）
5. 方向不相左（不白費投資、不走死路；非要求「強到能當碩論」）

刻意排除：視覺化揭露力 / 創新貢獻 / 文獻 gap 大小 / 領域熱度——皆為碩論尺度問題，會癱瘓選題

**5 候選打分**（1–5，加總 /25）：

| 角度 | A. Dyn 2D Rect | B. 2D Strip | C. Predictions | D. KV-cache | E. Failure Taxonomy |
|---|---|---|---|---|---|
| 1. Baseline 可實作 | 4 | 5 | 2 | 2 | 3 |
| 2. 問題鋒利度 | 4 | 3 | 5 | 4 | 3 |
| 3. 報告呈現力 | 5 | 4 | 4 | 3 | 5 |
| 4. 風險可控性 | 4 | 5 | 2 | 1 | 3 |
| 5. 方向不相左 | 5 | 3 | 5 | 5 | 4 |
| **加總** | **22** | 20 | 18 | 15 | 18 |

選 A 的核心：其他選項都有顯著弱項（B 動機弱、C/D 可行性弱、E metric 軟），A 五角度都不墊底

**視覺化角色定錨**（修正過頭講法）：
- 「視覺化改善 fragmentation」這個敘事框架本身不對位——演算法看數字不看像素
- 視覺化能載重的三種形式：(a) ML 輸入特徵（已封頂）；(b) HITL 介面 + 量化勝出；(c) algorithm steering / 過程動畫
- Special Topic 不靠視覺化貢獻立論；視覺化是觀察工具，主張落在「failure mode 觀察」或「heuristic 退化比較」

### 行動 to-dos（從本日決策衍生）

- [ ] 動手前 **2–3 天 positioning scan**（不深讀）：FPGA DPR 圈 + Multi-dim Dynamic BP 圈各 3–5 篇近期論文，主動回答三個問題以支持報告結尾的 next-step claim：
  1. 別人在 dynamic 2D BP 上**已優化過什麼**（家族 1 Online Placement Heuristics / 家族 2 Empty Space Maintenance / 家族 3 Compaction / 家族 4 Learning-Augmented 各自最新進展）
  2. 那些優化的**邊界在哪**——哪些 workload / failure mode 沒處理好
  3. 我預計的觀察可能落在哪個邊界外
  順便檢查 {heuristic 組合 × workload × metric} 不完全重複；若完全重複則微調 framing 而非棄題
- [ ] 第 1–2 週：2D BLF + 合成 arrival/departure baseline（Hopper-Turton benchmark 改造）
- [ ] 5/31 前：根據實作結果決定 narrative（A 原版 vs E 變體）
- [ ] 6/8 報告週前：8 成報告完成

### Special Topic 報告 bar 釐清（同日傍晚對話）

**設定的 bar**：不解決問題，但結尾必須立得起 next optimization target——能講出「現有方法已優化到 X、我觀察到的 gap 是 Y、下一步可從 Z 切入」。
- **不接受的下限**：報告結尾只能講「我觀察到 BLF 退化得比 FFS 嚴重」這類純比較——口試委員問「so what / 你怎麼知道別人沒做過」會答不上來
- **要做的支撐**：上方 positioning scan 是讓這句話有底氣的前置（沒這個定位，next-step claim 立不起）
- **對 narrative 選擇的隱含影響**：E 變體（failure mode taxonomy）比 A 原版（heuristic 退化比較）更自然對位此 bar——taxonomy 本身即 optimization target 選單，每個命名的 mode 對應一個下一步可 attack 的方向。但仍依 5/31 實作結果決定，不提前鎖死
- **報告結構草案**（5 段）：(1) Lit positioning 別人優化過什麼；(2) Gap 那些優化沒處理什麼；(3) Baseline 實作落入那個 case；(4) Observation 視覺化 + 量化 reveal 失敗結構；(5) Next-step claim「碩論將針對 [模式 X] 設計 [類型 Y] 改良」

### 仍待決定（已縮減）

- A 原版（heuristic 退化比較）vs E 變體（failure mode taxonomy）的 narrative（5/31 前定）
- 碩論場域（碩論階段決定）
- 是否約楊老師 sanity check Special Topic 方向
- 是否將本日轉折寫進 `journal.md`

### Dynamic 2D Rectangle BP 思考的關鍵釐清（尚未拍板方向，僅為理解層級）

**2D rect BP 領域成熟度**：
- 已封頂：offline 2D BP、online 2D BP（無離開）→ 純 heuristic 改良幾乎無貢獻空間
- 仍有空間：dynamic with departures + repacking cost、Learning-based（特別是 2D online with departures）、Multi-objective（取件時間／平衡／阻塞風險）、Domain-specific constraint richness

**視覺化的精確角色**：
- 給研究**速度**（找 single-instance failure pattern、加速直覺養成）
- **不給**研究**新穎性**——新穎性必須來自變體或場域
- 前一輪「視覺化能找出 baseline 看不到的問題」是過頭的講法，需修正

**load-bearing 視覺化的四種條件**（若要讓視覺化成為碩論主體而非配角）：
1. 視覺化作為演算法的**輸入特徵**（CNN/ViT 看 partial packing 預測下一步）
2. **HITL 結構性介面**（使用者鎖定、拖動、強制分組，抽掉視覺化系統不成立）
3. **跨 instance failure pattern mining**（image embedding 對失敗結果聚類）
4. **Algorithm steering / 過程動畫**（揭露搜尋過程的時序動態，而非靜態結果）

**時間尺度分離原則**：
- Special Topic（6/8）≠ 碩論貢獻；用碩論標準評 Special Topic 題目會導致選題癱瘓
- Special Topic 只需 presentable demo；碩論才需要填真實 gap

### 尚待決定的開放選項

- 是否接受「Special Topic 重新定位為 diagnostic survey（為碩論做的失敗模式地圖）」
- 是否走「場域變體」路線（碩論貢獻較可能）vs 純理論（成熟封頂，貢獻難）
- 若走場域變體，場域選擇：雲端 VM / 半導體 cassette / 倉儲 / 貨櫃堆場 / 零售貨架 / 製造 WIP buffer
- 是否約楊老師討論變體場域選擇（他可能有產學連結資訊）
- 是否將本次轉折寫進 `journal.md`

### 既有條目

- 建立 memory 系統，分為 research-decisions / progress / ideas / experiments 四類
- 採「兩者並存」策略：本專案內的 memory 系統跟 git；harness 自動 memory 維持在 `~/.claude/projects/.../memory/` 不動
