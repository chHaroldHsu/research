# 靈感與發想

> 紀錄研究點子、候選題目、跨領域聯想、未來可能延伸的方向。
> 格式：`## YYYY-MM-DD` 為段落標題，最新日期置頂。

---

## 2026-05-30

### 核心 idea 的 novelty 狀態修正 [已驗證 2026-05-30]

針對老師主軸（依某時刻 bin 狀態動態選最佳 heuristic／下棋比喻）做 prior-art 掃描 → **這個範式已存在**：就是 *selection hyper-heuristic*（Özcan-Parkes-Asta 的 policy-matrix / apprenticeship learning）+ *RL-for-BP*。下棋比喻 = RL 把狀態當 state、選 action 的標準框架。細節與引用 → literature-map 2026-05-30。

- 原本隱含的 [假設「依狀態選 heuristic 沒人做過」] → 作廢。
- **novelty 不在「動態選 heuristic」這件事，而在組合**：2D + departure/fragmentation + 可解釋的 workload-pattern→heuristic mapping（= 我的 mode taxonomy）+ 視覺化。對應本檔 2026-05-25 方向 C（per-timestep oracle）= 字面就是 RL 框架，要守住差異化必須掛在上述組合上。
- **存亡關鍵未結案**：2022–2025 有沒有人已做「2D DBP **with departure** + RL/HH 動態選法」尚未窮盡確認（5/30 直連被擋）。這條若被占走，per-timestep 動態選法的 framing 要再退一步靠 taxonomy/視覺化。→ 下輪精讀第一優先。

---

## 2026-05-25

### Oracle Gap = 0% → heuristic 集合需要擴充

用 seed_sweep_raw.csv（600 runs）算出 Oracle Gap：BLF 在 150/150 個 run（所有 workload × 所有 seed）全勝，Gap = Y − X = 0%。原因：BLF（幾何式）和 NFS/FFS/BFS（shelf 式）不是同等級的方法，shelf 天生放棄 y 軸自由度，PE 天花板低。

**結論**：現有 4 heuristic 無法支撐 dynamic switching narrative——oracle 永遠選 BLF，沒有「根據 mode 切換」的空間。

**未來實驗設計（讓 Oracle Gap > 0 的三個方向）**

- **方向 A：擴充幾何式 heuristic**（最優先）——加入 Maxrects、Skyline、Guillotine 等幾何式方法，讓同等級 heuristic 之間在不同 workload/mode 下互有勝負。這是讓 dynamic switching 成立的最直接路徑
- **方向 B：換 objective function**——從純 peak PE 改成複合指標（如 `PE − λ × discard_rate`），discard_rate 高的場景可能翻盤
- **方向 C：per-timestep oracle**——不是整場選一個 heuristic，而是每個 item 到來時根據當前 bin snapshot 選最佳 heuristic。更接近老師說的「下棋」比喻，但實作門檻較高，需要 real-time state feature extraction

**與老師 5/25 meeting 的連結**：老師建議的主軸是「根據棋盤狀態動態選策略」，Oracle Gap = 0% 說明現有 heuristic 集合不足以展示這個價值。方向 A 是讓此主軸成立的前提條件。→ decisions 2026-05-25

---

## 2026-05-23

### 從前置 #2–#5 副產物冒出的延伸方向

由 30-seed sweep + cluster 分析（→ exp 2026-05-23）冒出 3 個非當前報告主軸、但值得未來追的方向：

**時序 signature（補回 peak 丟掉的時間維度）**
- 發現 light_dep 與 heavy_dep 在 peak signature 上等價（d/σ ≤ 0.16，跨所有 heuristic）→ peak 信號完全丟掉了 departure rate 差異
- 補回時間維度的候選 metric：turnover rate at peak（peak 時刻的進出 item 速率）、time-to-peak（首次達到 peak PE 的 tick）、peak duration（PE 停在 ≥ 95% peak 的時長）
- 這些 metric 應該能區分 light vs heavy。如果區分得出來，signature 從 2D 擴成 4D（peak_pe / discard / turnover / duration），mode taxonomy 可能新增 transient-only mode
- 對進階 6（RL feature）相當友善：時序 metric 本來就是 state 的一部分

**FFS ≡ BFS 在當前參數區的條件**
- 4 個 metric 全部成立的等價需要可解釋的原因。猜想：bin/item size 比較小 → shelf 候選數少 → first-fit 與 best-fit 常選到同一個
- 未來可掃 bin/item 比，找出 FFS 與 BFS 開始分離的 threshold
- 對碩論：bin 大小 sensitivity sweep 是必做（5/19 已 flag），這個 finding 是它的子目標

**Grid topology signature（救回 Inland Island）**
- 當前 Inland Island 退場是因為 (peak_pe, discard, mean/peak) 三維 signature 抓不出「中央 trapped voids」
- 救法：對 peak grid 做 connected-component 分析，分離 boundary void（接觸 bin 邊界）vs interior void（被 item 包圍）。interior void count / total void area ratio 可能是 Inland Island 的有效 detector
- 風險：要寫額外 topology code，且 mode 是否真存在還是要視覺確認。當前報告先不做，留作碩論細化的選項

---

## 2026-05-14

### 變體 E（failure mode taxonomy 失敗模式分類學）的未來延伸方向

Special Topic 階段只實作 taxonomy 本身；報告結尾明示「未來可往 6 / 8 兩條 map（對應）」，作為碩論候選方向。

**進階 6：Mode 當 RL state feature（模式作為強化學習狀態特徵）**
- 把命名的 failure mode label 加進 RL agent（強化學習代理）的 state representation（狀態表示）
- 給 agent 注入 inductive bias（歸納偏置）：看到「目前 mode = Sliver」→ 學對應策略
- 預期 sample efficiency（樣本效率）勝過無 mode 標籤的純 baseline
- 風險：依賴 RL 訓練本身能跑；對楊老師方向不直接對齊（偏 ML 系統）

**進階 8：Cross-domain transfer（跨領域遷移）**
- 把 abstract taxonomy 套到具體場域，驗證 mode 是否普適：
  - FPGA partial reconfiguration（部分重組）
  - Cloud VM placement（雲端虛擬機調度）
  - KV-cache fragmentation（鍵值快取碎片，LLM 推論）
- 若跨域出現相同 mode 集合 → taxonomy 升格為 universal framework（普適框架）
- **與 5/12「碩論場域延後」決策的耦合點**：cross-domain 驗證流程恰好是「實驗驗證後再選場域」的天然路徑——做 cross-domain scan，看哪個場域最容易產生 distinct mode、最對接產學連結，再鎖場域

**為什麼挑 6 + 8 而非 1/2/3/4/5/7**：
- 6 = ML 系統路線天花板（潮、影響力高）
- 8 = 場域路線天花板（與碩論場域選擇直接耦合，且保留選擇權）
- 1/2/3 偏戰術改良，可被 6 或 8 吸收（mode-aware policy 可由 RL agent 學出）
- 4 偏視覺化補強，當 E 主體已涵蓋
- 5/7 偏 OR 理論，不符合 GIMT 系所定位

---

## 2026-05-12

### Dynamic 2D BP 仍有空間的方向（變體候選軸）

- **Dynamic with departures + repacking cost**：item 會離開、重排有成本、是否該重排是 meta-decision。比 online（只進不出）少很多 paper
- **Learning-based（2D online with departures）**：Deep RL / imitation learning，比 3D static（Zhao 2021、AlphaPack 等已熱）冷門
- **Multi-objective**：BP 文獻多只看 utilization，實務還要看取件時間、平衡、阻塞風險、退化／時效
- **Domain-specific constraint richness**：堆疊高度限制、易碎品分隔、溫區、出貨順序、due date、AGV 走道留白——每多一個都讓 textbook heuristic 失效

### 可能的應用場域（待文獻探索 + 老師討論）

- 雲端 VM placement（資料公開、模擬器成熟）
- 半導體 cassette buffer / FOUP 儲位
- 倉儲動態儲位（含 ABC 分級、揀貨頻次）
- 貨櫃堆場 / yard planning
- 零售貨架補貨
- 製造業 WIP buffer（已寫入 `context/research-interests.md` 第 3 節的場域遷移構想）

### load-bearing 視覺化的四種角色

詳見 `research-decisions.md` 2026-05-12 段。重點：若希望視覺化在碩論裡是必要而非裝飾，需走 CNN feature extractor、HITL 介面、image-embedding failure clustering、或 algorithm steering 其中一條。

### 既有條目

- 初始建立檔案，Bin-Packing 候選題目詳細分析請見 `candidate-topics.md`
