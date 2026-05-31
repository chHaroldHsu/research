# 研究決策

> 紀錄研究方向的關鍵決策、放棄的方向、選題理由。
> 格式：`## YYYY-MM-DD` 為段落標題，最新日期置頂。

---

## 2026-05-30

### 方法論決策：per-timestep oracle 定義（未來實作前必須先拍板）

對話釐清「per-workload oracle Gap = 0，per-timestep 還會不會 > 0」——核心結論：**per-timestep oracle ≥ per-workload oracle**（前者決策空間是後者嚴格超集），所以 per-workload = 0 不代表 per-timestep = 0；但兩個 oracle 在現有 heuristic 集合（BLF 跨 5 workload 平均勝下一名 24.6 pp）下，per-timestep gap 即使 > 0 也很可能小到不足以撐 narrative。仍應先擴 heuristic 集合再上 per-timestep。→ ideas 2026-05-25 路徑 C、decisions 2026-05-25

**Per-workload vs per-timestep oracle 差別**：

- Per-workload：事先知道 workload type，整場鎖一個 heuristic。決策粒度 = 每 run 一個（150 個決策點 / 600 runs）。對應問題「事先知道是 light_departure，應該選誰一路跑到底？」
- Per-timestep：每個 item arrival 來時看當下 bin state 為這顆 item 選 heuristic，下一顆可能換。決策粒度 = 每 item 一個（n=200, 30 seed, 5 preset → 30000 個決策點）。對應老師「下棋」比喻——每步看盤面選招
- 數學關係：per-timestep oracle 至少能模仿 per-workload oracle（每步都選同一個），所以 Gap(per-timestep) ≥ Gap(per-workload)

**Per-workload = 0 不蘊含 per-timestep = 0 的情境**：

- 情境 A（per-timestep 也 = 0）：BLF 每一步都是當下最佳選擇，不是只贏在累積平均
- 情境 B（per-timestep > 0）：BLF 贏在累積但個別時刻 myopic 失誤。例如 bin 半滿剩一塊細長空間，BLF 為塞當下 item 切碎那塊空間；改用 BFS 開新 shelf 短期 PE 降一點，但保住未來 large item 容納空間。整場 BLF 還是贏，但某些時刻換手更好

**Why 仍要先擴 heuristic 集合而非直接做 per-timestep**：BLF 對下一名差 24.6 pp 是結構性弱點（shelf 放棄 y 軸自由度），不是某幾步失誤造成的。在這種懸殊差距下，per-timestep gap 即使 > 0 也很可能是噪音級，要說服 reviewer「動態切換有價值」碩論慣例至少 3–5 pp gap。先讓 per-workload Gap > 0，per-timestep 才有顯著放大空間。

**Per-timestep oracle 的三個必須拍板的設計選擇**（實作前要先定義清楚，不然 Gap 數字無法解讀）：

- **Lookahead 範圍**：oracle 看 1 步、k 步、還是看完整 future arrival/departure schedule？看越遠越強，但越遠越偏離「dynamic online」設定。Clairvoyant（看穿整段 future）對應 decisions 2026-05-18 RL 評估的「Offline clairvoyant optimal」層，是理論上界
- **Switching cost / state handoff**：item 已被 BLF 擺進 bin，下一步換 NFS，NFS 內部 state（哪些 shelf 已開、x-cursor 位置）如何初始化？BLF 的擺放對 shelf state 沒貢獻，硬切換會讓 shelf heuristic 從錯誤 state 起跑
- **Beam vs greedy**：每步真的窮舉 4 個 heuristic 各跑完整場再回溯（NP-hard 級算力，只能小實例），還是 1-step greedy + 啟發式評估下一步？前者是理論定義，後者是實務 proxy

**Clean 理論定義（推薦作為報告基準）**：每個 item arrival 時刻 t，對每個 heuristic h 都把該 item 用 h 擺一次，然後從 t+1 開始用該 h 跑完剩餘 trajectory；取最終 peak PE 最高的 h 當作 t 時刻 oracle 的選擇。這是 lookahead = 整段 future + greedy switch 的版本，算力 O(H × N × T) per run（H heuristic 數、N item 數、T sim 時間）。對 n=200 量級可行但要 batch run。

**How to apply**：未來真的做 per-timestep oracle 時，報告必須在 method section 明示三個選擇（lookahead 範圍 / switching cost 處理 / 評估方式），且基準版用 clean 理論定義；如果實務上太慢，再加 ablation 比「greedy 1-step」「k-step lookahead」與「clairvoyant」三檔差距。任何沒明示這三項的 per-timestep gap 數字都站不住腳。

---

## 2026-05-25

### 老師 meeting：主軸確認 + Oracle Gap 實測結果

**老師建議的主軸**：找出每個 workload 下的 pattern，未來能根據某一時刻的 bin 狀態動態選擇最佳 heuristic——類似 ML 下棋，每步根據棋盤狀態選最優行動。此方向與既有 GT 三層架構（→ decisions 2026-05-22）的 Prescriptive 層直接對應。

**Oracle Gap 實測**：用 seed_sweep_raw.csv（4 heuristic × 5 preset × 30 seeds = 600 runs）計算，結果 Gap = 0%。BLF 在 150/150 個 run 全勝，oracle 永遠選 BLF。原因：shelf 家族（NFS/FFS/BFS）與幾何式 BLF 不在同一等級。

**待決**：要讓 dynamic switching narrative 成立，需擴充 heuristic 集合（加入 Maxrects / Skyline / Guillotine 等幾何式方法），使不同 heuristic 在不同 mode 下互有勝負。→ ideas 2026-05-25

---

## 2026-05-22

### 方法論決策：E variant 的 ground truth 三層驗證架構

對話釐清「我的 ground truth 是什麼？比較對象是誰？」核心結論：**E variant 是 descriptive science，沒有 single ground truth；要靠三層 validity 遞進驗證**。常見的「找一個 baseline 對打」思維不適用——那是 prescriptive 階段才有的問題。

三層 validity 遞進：

- **階段 1（現在做的）descriptive**：GT = mode 在 signature 空間可區分 + 覆蓋完整。當前 narrative 對應 4×5 sweep + 6 mode 命名。
- **階段 2（報告 punchline）predictive**：GT = 早期 signature 可預測最終 mode。當前 narrative 對應 oracle gap（下一段）。
- **階段 3（進階 6 / 8）prescriptive**：GT = mode 知識改善決策（RL or hand-designed mitigation）。當前 narrative 對應進階 6 mode-as-RL-feature。

現階段（descriptive）GT 三件事：

- **Distinguishability** — 跨 seed 的 mode signature cluster 緊、mode 間距離大（silhouette / DB index 可量化）
- **Completeness** — 每個 (heuristic × workload) cell 都能標到 mode；標不出來強迫新增 mode 或承認 taxonomy 不完整
- **Utility** — 至少做到 predictive validity，最好做到 prescriptive oracle gap

### 方法論決策：Oracle Gap 作為 Special Topic 報告 punchline

報告結尾的可交付數字，同時做兩件事：證明 mode 資訊有量化價值（E 的 GT），以及給進階 6 RL 一個明確 target。

定義：

```
X = single-best heuristic 跨 5 workload 平均 peak PE
Y = mode-aware oracle（事先看穿 mode、選 best heuristic per workload）平均 peak PE
Oracle Gap = Y - X  ← mode 資訊的價值上限
```

對應到 2026-05-18 RL 四層 baseline：oracle gap 就是「mode-aware upper bound」這層，跟「vanilla RL」之間的差距是進階 6 要去吃的空間。→ see decisions 2026-05-18 RL 評估的兩層架構。

Narrative 收斂句（不承諾 RL 結果，只立 next-step target）：
> 「Mode 資訊的價值上限是 Gap = Y - X。進階 6 將檢驗 RL agent 能吃下這個 Gap 的多少比例。」

### 重要修正：PE 方向

PE = packing efficiency，**越高越好**。mode-aware 改善的方向是更高 PE / 更低 discard / 更低 F，不是「更低 PE」。任何寫到「更低 PE」是 typo，要當下糾正。

### 方法論決策：用 paired comparison 應對「無共識 benchmark」

對話釐清「dynamic BP 沒共識 benchmark，workload 一變絕對數字就漂移，怎麼做 ablation？」——核心結論：**ablation 比的是「同 workload 上兩方法的差」，不是絕對 PE；paired gap 對 workload sensitivity 免疫**。

問題背景：dynamic BP 工作負荷可變維度多——bin H×W、item size 分布、arrival rate λ、lifetime 分布、是否 burst——任一軸動絕對 PE 都會大幅漂移。Hopper-Turton 在 static 是共識，加上 arrival/departure 後就沒了。跨 paper 報「peak PE = 73.5%」這種數字幾乎沒比較意義。

為什麼 ablation 不被摧毀：

- 比的是「vanilla 對 mode-aware 在同一 workload 上的 gap」，不是絕對值
- 範例：W1 上 vanilla 68% / mode-aware 73% → gap +5pp；W2 上 vanilla 52% / mode-aware 57% → gap +5pp。絕對值 68/52 不能比，但 gap +5/+5 可以比
- Gap 不穩本身就是 finding：「mode 資訊在哪類 workload 起作用、在哪類失效」

三層應對策略：

- **Workload axis 變成研究變數**：4×5 factorial 已經在做。Workload 不是「隨便挑一個」是「刻意 sweep」。未來 RL ablation 同樣設計——訓練 workload 鎖定 declare，**測試時跑全部 5 種**，加 train-on-X-test-on-Y matrix 看 generalization。
- **報 relative gap 不報 absolute**：論文 claim 應該是「相對 vanilla 改善 7pp [CI 5–9]，在 small-item 上不顯著（1pp [-1, 3]）」，不是「mode-aware PE = 73%」。第一種句型對 workload sensitivity 免疫。
- **Sensitivity curves**：gap vs λ、gap vs lifetime、gap vs item-size-mean、gap vs item-size-variance 各畫一條。Reviewer 最在意「方法在什麼條件下有效」。例：「mode-aware 在 churn 0.3–0.7 單調改善，> 0.8 飽和」這個 finding 本身就是貢獻。

Oracle Gap 的特殊性質：

- X = single-best heuristic PE、Y = mode-aware oracle PE，**同 workload 上算**，gap = Y - X 是 paired difference
- Workload 變難或變易，X 和 Y 同向漂，gap 可能仍穩定
- Gap 不穩定的時候本身就是「mode 資訊在這類 workload 價值更高」的訊號
- 比直接 claim「Y = 70%」robust 一個量級

Mode-level 比 PE-level 更 robust（尚未充分利用）：

- PE = 70% 在不同 workload 下意義天差地別
- 但「BLF 在 large_items 下出現 Brick-wall mode」這個結構性陳述跨 workload 穩定——只要 item-size mean 過 threshold，brick-wall 就會出現
- Mode taxonomy 的 claim 本質是 **conditional structural**（「在條件 C 下出現結構 S」），對 workload sensitivity 抗性強過 numerical performance

未來 RL ablation 的具體實驗設計清單：

- 訓練 workload 嚴格 declare（H×W、item 分布、λ、lifetime——一行 reproducibility note）
- 每 cell ≥10 seeds，報 mean ± std
- 5 workload 全測，產 gap matrix 不是單一數字
- Sensitivity curves：在訓練 workload 周邊掃 λ、lifetime 各 5 點
- OOD 測試：用沒訓練過的 workload，看 gap 衰減多快
- Negative results 也報：哪幾個 workload 上 mode-aware 沒贏 → 反而增加可信度

→ 與本日「GT 三層架構」「Oracle Gap」「2026-05-18 RL 評估多軸」三段互相補強：所有「比較」的可信度都建立在 paired same-workload comparison 之上。

### 方法論決策：命名 mode 前的 4 項前置驗證

對話釐清「目前是否真能說 workload 量化得出 fragmentation pattern」——核心結論：**現有 4 數字 signature 撐不起這個 claim，命名 mode 前必須先補 4 件事**。不補就命名等於把 seed=42 的單次觀察當證據。

四項前置驗證（全部可用現有 4 heuristic × 5 preset 程式跑，不動 simulator）：

1. **F@peak / mean/peak 跑滿 10 seeds**：目前這兩個 signature 元件只有 seed=42 一次觀察。`seed_sweep.py` 已跑 200 runs，CSV 加 2 欄即可，給 mean ± std。
2. **Mode 視覺穩定性檢驗**：6 個 mode 候選是看 seed=42 那張 4×5 圖讀出來的。要 loop 10 seeds 各畫一張 4×5，紀錄每個 mode 出現比例（例如「Inland Island 9/10 seeds」）。穩定 < 6/10 的 mode 視為 seed artefact 退場。
3. **Signature 空間分離檢定**：把 200 runs 的 4 數字當點，在 signature 空間做 cluster / scatter（PCA 或 任兩維），看不同 (heuristic × workload) cell 是否分群、還是雲糊在一起。這對應 [[GT 三層架構]] 的 Distinguishability。
4. **Heuristic-intrinsic vs workload-induced mode 區分**：跨 5 preset 都出現的視為 heuristic-intrinsic（如 BLF brick-wall、shelf stripe），只在 1–2 preset 出現的才算 workload-induced。研究真正貢獻在後者；前者降級為 baseline behavior。

**Why**：E 變體的 narrative 是「workload 量化得出 mode」，現在 4 數字裡有 2 個只有 n=1 seed、6 個 mode 候選沒做 reliability check、沒做統計分離、沒區分 heuristic vs workload 的貢獻。命名 mode 之後才被楊老師或 reviewer 問起這 4 點代價遠高於現在補完——尤其 #4，命名之後再砍 mode 會打亂整個 narrative 結構。

**How to apply**：第 4 週流程從「prior work → 命名 mode → signature → mitigation → oracle gap」改為「prior work + 4 項前置 → 命名 mode → ...」。前置 #1–#2 跟 prior work 細讀可並行（CPU 不衝突）。

**Fallback 評估**：如果 #2 砍掉一半 mode（剩 3 個）仍 ≥ 3 門檻，narrative 安全。如果 #4 後 workload-induced mode = 0（全是 heuristic-intrinsic），narrative 轉向「heuristic family signature 跨 workload 穩定」——本身就是發現，Oracle Gap 仍可算（best-per-workload 對 best-overall），進階 8 cross-domain 不受影響、進階 6 RL-feature 失基。再差到 signature 雲糊在一起（情境 C），Special Topic 轉成「方法論診斷 + 負面結果」報告，仍符合 bar。

---

## 2026-05-18

### 方法論決策：RL 評估的兩層架構（為進階 6 鋪設）

對話釐清「RL 結果要基於 optimal 來優化嗎？」——拆成訓練 vs 評估兩件事。

**RL 訓練不需要 optimal 標籤**：RL 不是 supervised learning，靠 reward signal 自己探索。mode label 是當 state feature 注入 inductive bias，不是當監督 label。

**RL 評估的對照分層**（dynamic BP 下「optimal」是模糊的，要分層）：

| 比較對象 | 怎麼算 | 用途 |
|---------|--------|------|
| Offline clairvoyant optimal | 預知整段 arrival/departure，IP solver 求事後最佳 | 理論上界；只能對小實例（n ≤ ~50） |
| 強 heuristic baseline | BLF / Shelf / FFDH 直接跑 | 實務 floor |
| Prior RL baseline | Burcea 2014 / Wei 2011 / Powers 2023 | 直接競品 |
| **Vanilla RL（無 mode feature）** | 同 agent 架構但拿掉 mode | **關鍵 ablation——賣點所在** |

**核心原則**：賣點是「相對於 vanilla RL 的改善」，不是逼近 clairvoyant optimal。Optimal 只在小實例當天花板參照，告訴 reviewer 整體還有多少空間。

### 方法論決策：RL 評估的多軸選擇（不只是收斂速度）

mode-aware RL 的 inductive bias 設計，預期改善的不是 final PE 而是後幾軸：

| 評估軸 | 量化方式 | mode-aware 預期 |
|--------|---------|----------------|
| Final PE | 收斂後 PE | 不一定贏（vanilla 樣本夠多也可能學到隱式 mode） |
| **Sample efficiency** | 達到 X% PE 所需 env steps | **大概率贏**——最自然的 inductive bias 賣點 |
| **Generalization** | OOD workload（沒訓練過的分布）上的 PE | **可能贏**——mode signature 比 raw state 更 transfer |
| **Robustness** | 跨 seed / 跨 workload 的 variance | **可能贏**——state 更 informative |
| **Hard-case performance** | mode 集中出現的 instance 上的 PE | **應該贏**——inductive bias 設計目的 |

**故事設計**：4–5 行的 ablation 表，故事是「X 軸明顯贏、Y 軸打平、Z 軸略輸但代價合理」。不要單押 final PE，那是 vanilla RL 最容易追上的軸。

### 方法論決策：NP-hard 問題的參數設定（三層架構）

問題的核心：不同參數 regime 下 BP 演算法行為完全不同，平均成一個數字會洗掉所有資訊。

**Layer 1：用 benchmark instance family，不要自己亂生**

| Benchmark | 特點 |
|-----------|------|
| Hopper-Turton (1999/2001) | 從已知 optimal 切出 instance，**OPT 已知** |
| Berkey-Wang (1987) | 10 個 class，item size 分布不同 |
| Martello-Vigo (1998) | 4 個 class，更刁鑽 |

Dynamic 2D BP **沒有公認 benchmark**——要明確定義「改造 Hopper-Turton 變 dynamic 的方式」並公開，讓後人可複製。這是義務也是機會。

**Layer 2：對制度參數做 factorial sweep**

Dynamic BP 影響難度的關鍵參數：
- Item size 分布（小 item vs 大 item 主導）
- Aspect ratio 分布（正方形 vs 細長）
- Lifetime 分布（短壽 vs 長壽、指數 vs heavy-tail）
- Arrival rate / load factor（稀疏 vs 飽和）
- Departure 是否預先知道（clairvoyant lifetime vs unknown）

每個參數定 2–3 個 level，所有方法跑同一套 instance。產出「方法 × 參數設定」表格。

**Layer 3：報告時做 stratification，不要平均後比**

不同 regime 不同方法贏：
- Light load → 都接近 OPT，比不出差異
- Medium load → 演算法差異最明顯
- Heavy load → 都崩，比誰崩得慢

報告格式按 regime 切：

```
Load level    BLF    Shelf   Vanilla RL   Mode-aware RL
Light (0.3)   0.95   0.96    0.97         0.97         ← 都差不多
Medium (0.6)  0.78   0.82    0.85         0.89         ← 賣點在這
Heavy (0.9)   0.55   0.62    0.61         0.71         ← 賣點更大
```

### 與 E 階段的連動

E 階段 failure mode taxonomy 正是 Layer 2/3 的前置工作：「在 (item-dist × lifetime-dist × load) 的哪個 regime，哪個 heuristic 出現哪個 failure mode」。Taxonomy 一旦建好，進階 6 的 RL 實驗就有現成 regime 切分依據——不是隨便切 light/medium/heavy，而是按發現的失敗模式切，比一般 RL 論文紮實。

**E 階段量化（區別於進階 6）**：
- E 量化 mode 的可辨識性 / 覆蓋率 / signature 一致性，**不是 beat baseline PE**
- 進階 6 才回頭比 PE / fragmentation，且主軸是 mode-aware vs vanilla RL 的 ablation

### Heuristic 集從 {BLF, NFDH, FFDH, Shelf} 改為 {BLF, NFS, FFS, BFS}

**動機**：NFDH / FFDH 名字裡的 "DH"（Decreasing Height）需要先把所有 item 按高度遞減排序，這是**offline** 假設——在 dynamic online + departure 設定下做不到（不知道未來 item）。本研究刻意鎖 online（item 一個個來、來了就要放、不能 buffer），所以 textbook NFDH/FFDH 不適用。

**新集合（皆 online shelf 家族）**：
- **NFS**（Next-Fit Shelf）：只看當前最近開啟的 shelf；不夠就開新的
- **FFS**（First-Fit Shelf）：依開啟順序掃所有 shelf，第一個塞得下就用
- **BFS**（Best-Fit Shelf）：所有能放的 shelf 中選「剩餘高度最小」者

**Shelf 語意（textbook 純粹版）**：x-cursor **只前進不回退**——shelf 內 item departure 留下的 cell 不可重用。這正是要觀察的失敗模式（候選 "Departed-item Ghost" / Top-Shelf Waste），不是 bug。

**未取 NFDH/FFDH 作 offline upper bound 對照**：實作 + 解讀成本上升；narrative 也會被「online vs offline 差距」分散注意力。若第 3 週發現需要量化「online 損失多少」，再考慮加。

> SUPERSEDED 2026-05-25：Oracle Gap = 0% 證明需擴充幾何式 heuristic（Maxrects / Skyline / Guillotine）→ see decisions#2026-05-25、ideas#2026-05-25
~~**為何 4 個夠不另加 Skyline**：BLF 已是無 shelf 結構的代表，BFS 與 FFS 形成「best vs first」對照組，4 個已涵蓋「無結構 / 順序開啟 / 緊湊匹配」三軸。Skyline 與 BLF 重疊度高，先省下。~~

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

> SUPERSEDED 2026-05-18(晚)：4×5 factorial sweep 跑出後，候選 mode 已從 4 個擴為 **6 個從圖直接讀出**（Brick-wall / Horizontal stripe / Inland Island / Top sliver / Shelf abandonment / Item-too-tall failure）。原 4 名中只有 Inland Island 保留，其餘三個（Sliver Strip / Boundary Lockout / Staircase Skyline）**未驗證即被新觀察取代**。→ see experiments 2026-05-18(晚)。本段方法論原則（假設 vs 結論）仍有效。

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

> SUPERSEDED 2026-05-14：narrative 提前收斂至 E 變體 → see #2026-05-14。碩論場域維持延後決策。**仍未決**：約楊老師 sanity check、寫 journal.md。

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

> SUPERSEDED 2026-05-14：前 4 個選項已拍板——E 變體 = 對應「diagnostic 失敗模式地圖」；abstract framing 取代「場域變體 vs 純理論」二選一；場域選擇延後到碩論階段（5/12 即決）。**仍未決**：約老師 sanity check、寫 journal.md。

- 是否接受「Special Topic 重新定位為 diagnostic survey（為碩論做的失敗模式地圖）」
- 是否走「場域變體」路線（碩論貢獻較可能）vs 純理論（成熟封頂，貢獻難）
- 若走場域變體，場域選擇：雲端 VM / 半導體 cassette / 倉儲 / 貨櫃堆場 / 零售貨架 / 製造 WIP buffer
- 是否約楊老師討論變體場域選擇（他可能有產學連結資訊）
- 是否將本次轉折寫進 `journal.md`

### 既有條目

- 建立 memory 系統，分為 research-decisions / progress / ideas / experiments 四類
- 採「兩者並存」策略：本專案內的 memory 系統跟 git；harness 自動 memory 維持在 `~/.claude/projects/.../memory/` 不動
