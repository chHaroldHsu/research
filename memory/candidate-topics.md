# Bin-Packing 候選題目

> 篩選判準：**Coffman 分類軸 × 視覺揭露力 × 一個月可行性**
>
> 視覺揭露力 = 視覺化能 reveal 什麼純數字看不出的結構（非「演算法結果好不好看」）

---

## 候選 A：Dynamic 2D Rectangle Bin Packing（軸組合：Dynamic × 2D 矩形）

> **Framing：「Tetris with departure」** — 矩形 item 流入指定容器，**有些會在隨機時間消失**，看演算法在會「留洞」的環境下怎麼決策。

- **軸組合說明**：時序軸選 Dynamic（有 arrival + departure），維度軸選 2D 矩形；其他軸取 classical（fixed-size bin、unbounded space、min bins、無 item 限制）
- **為什麼是這個組合**：
  - 純 Dynamic 1D（Coffman-Garey-Johnson 1983 原始版）gap 太薄
  - Dynamic × 2D 矩形組合在文獻中**意外稀疏**，視覺化作品幾乎為零（"dynamic bin packing visualization" 搜不出專門工具）
  - 2D 維度讓「碎片化模式」在俯視角下**無遮擋**呈現，視覺揭露力比 3D 強（見下方 2D vs 3D 比較）
- **Coffman 分類**：時序 = Dynamic（CGJ 1983 提出）；維度 = 2D 矩形
- **視覺揭露**：bin 填滿後因 item 離開出現「碎片化空隙」— 在 2D 俯視角下空隙形狀和分布完全可見。可同時跑 First-Fit / Best-Fit / Any-Fit + 2D placement（BLF / Shelf），看碎片化模式怎麼**質**上不同
- **理論深度**：Dynamic 競爭比的證明因 departure 而改變；2D placement 策略仍有 heuristic 改良空間
- **可行性**：1.5 週可生 baseline（2D BLF + 隨機 arrival/departure 合成資料）
- **入門文獻**：
  - Coffman, Garey, Johnson (1983) — Dynamic BP 原始定義與基礎結果
  - Wong, Yung — Online dynamic bin packing 系列
  - Online Multi-dimensional Dynamic Bin Packing (CIAC 2013) — 多維 dynamic 起點
  - Lodi, Martello, Vigo (2002) — 2D placement 啟發式

## 候選 B：2D Strip Packing — 啟發式並列比較

- **Coffman 分類**：2D 維度 + offline / online 都有經典結果
- **視覺揭露**：NFDH / FFDH / BL / BLD 並排跑同一份 input，**看出**為什麼 FFDH 結構性比 NFDH 好（不是比率，是「空間怎麼被浪費」的結構）
- **理論深度**：absolute vs asymptotic ratio、shelf-based vs guillotine 的取捨
- **可行性**：最高。BLF 一晚可寫完，benchmark 公開（Hopper-Turton 2001, Berkey-Wang 1987）
- **入門文獻**：
  - Lodi, Martello, Vigo (2002) — *Recent advances on two-dimensional bin packing problems*
  - Coffman, Galambos, Martello, Vigo (1999) survey

## 候選 C：Online BP with Predictions（Learning-Augmented）

- **Coffman 分類**：Coffman 2013 未收錄，是 2020 後的新分支
- **視覺揭露**：prediction error → packing 結果是非線性、非單調的函數，視覺化 trade-off frontier 是天生議題
- **理論深度**：當前最熱方向之一（consistency / robustness / smoothness 三軸取捨）
- **可行性**：中等。1D 版可做，但「預測模型 + 演算法」雙層 baseline 一個月偏緊
- **入門文獻**：
  - Im, Kumar, Qaem, Purohit (2021) — 入門切入點
  - Lykouris, Vassilvitskii (2018) — learning-augmented framework
  - Mitzenmacher, Vassilvitskii (CACM 2022) — *Algorithms with predictions* 綜述

## 候選 D：KV-cache Fragmentation Visual Atlas（軸組合：Dynamic × 1D paged blocks，LLM serving 應用）

> **Framing：「PagedAttention 之後，KV-cache 還剩什麼碎片」** — 不同 allocation / eviction 策略在不同 LLM serving workload 下產生的碎片化質性差異，系統性視覺化比較。

- **軸組合說明**：時序軸 = Dynamic（request arrival + token decode + completion + eviction），維度軸 = 1D paged blocks（PagedAttention 後）或邏輯 2D（位址 × 時間），bin = GPU HBM 的 fixed-size block pool
- **為什麼是這個組合**：
  - 候選 A 的 dynamic 2D rectangle 在當代雲端的**真實對應物**（領域熱度遠勝 FPGA DRP）
  - 2024+ 論文密集（vLLM、ORCA、Splitwise、DistServe、Mooncake），但**都在比 throughput 數字，沒人系統性視覺化策略間的碎片化質性差異**
  - 視覺化空白落在「**演算法比較**」這條軸；「debugging 工具」（PyTorch profiler、Nsight）已成熟，但無法切換 placement policy 做 reveal
- **Coffman 分類**：時序 = Dynamic；維度 = 1D paged blocks（嚴格說不是 rectangle 2D，但 (位址 × 時間) 視覺呈現等同 2D）
- **視覺揭露**：
  - 內部碎片（block 內未填滿位置）+ 時間碎片（block 持有時間）+ 多 request 並發下的格局演化
  - eviction / preemption 決策後留下的「疤痕」累積
  - workload regime（短請求多 vs 長 context、burst vs 穩定）與 policy 的 fit / misfit 模式
- **理論深度**：可導入新的碎片化 quality metric（不只 utilization）；可提出 workload-adaptive heuristic（block size、eviction ordering、length-aware admission）
- **可行性**：simulator-first 路線，1 個月可生 baseline simulator + 視覺化原型；**不需要 H100 叢集**，CPU + 小 GPU 即可
- **入門文獻**：
  - Kwon et al. (SOSP 2023) — vLLM / PagedAttention（baseline，必讀）
  - Yu et al. (OSDI 2022) — ORCA continuous batching
  - Patel et al. (ISCA 2024) — Splitwise（prefill-decode 分離）
  - Zhong et al. (OSDI 2024) — DistServe
  - Qin et al. (2024) — Mooncake
- **資料**：BurstGPT、Mooncake trace、Azure LLM Inference trace（皆公開）
- **與候選 A 的關係**：相同研究框架（dynamic BP heuristic 比較 + 視覺化驅動），不同 home application。FPGA DRP = 「真實 2D 矩形 + 領域偏冷」；KV-cache = 「1D paged blocks + 領域火熱」
- **風險**：
  - 領域論文每月在出，**特定 heuristic 改良容易被 scoop**（防禦：方法論貢獻——「視覺化驅動的策略比較」——不易被 scoop）
  - 學習曲線：要先吃 transformer 推論基本流程（KV-cache 是什麼、為何 attention 需要它、continuous batching 機制）
  - 老師（楊傳凱）專長為視覺化非 ML systems，系統知識需自學

---

## 維度選擇：為什麼候選 A 鎖在 2D（而非 3D）

| 面向 | 2D Dynamic | 3D Dynamic |
|---|---|---|
| Baseline 時程 | 1–1.5 週 | 2–3 週 |
| 實作複雜度 | 中（2D 碰撞 + BLF）| 高（3D 碰撞、旋轉、穩定性、camera/rendering）|
| 第一眼視覺衝擊 | 中 | 高 |
| 「揭露」視覺深度 | **高**（俯視全貌，碎片一目了然）| 中（**有遮擋**，內部空隙看不到）|
| 演算法成熟度 | 啟發式完整（NFDH / FFDH / BLF）| 較分散，多 variant |
| Benchmark 可用性 | 多（Hopper-Turton、Berkey-Wang 可改造加 departure）| 少，多為 static |
| 視覺化前人作品 | **少**（dynamic 2D 動畫罕見）| 多（static 3D YouTube 一堆，要做出差異）|
| 工程負擔（非研究的）| 低（D3 / canvas 即可）| 高（three.js / Babylon / Unity）|

### 三個反直覺重點

1. **「3D 視覺更強」是錯覺**：3D 一旦 item 多就有遮擋（occlusion），內部空隙看不到。2D 俯視 ground truth、碎片化形狀和分布毫無遮擋。3D 適合「裝載秀」，2D 適合「碎片化分析」 — 若研究主張是「視覺揭露純數字看不到的結構」，2D 服務更好

2. **3D 增加非研究貢獻的工程負擔**：three.js 的 camera、lighting、shadow、orbit 都要處理；做完很漂亮但口試委員不算進演算法貢獻。寫了一個月 rendering、研究只剩兩週是常見學生陷阱

3. **dynamic BP 視覺化整體稀缺**：無論 2D 或 3D，dynamic BP 動畫工具幾乎為零。所以「視覺化文獻空白」是這個題目本身的特性，**不是 2D vs 3D 的差異點**；2D vs 3D 的真正差異在前兩點（遮擋 + 工程負擔）

### 結論

3D 不是不能做，是**留作論文後期擴展**（碩論常見的 extension 章節）。從 2D → 3D 是 incremental，從 3D 退回 2D 等於認賠。

---

## 實際問題與主流方法（2D Dynamic BP）

> 視覺化只是呈現，背後要有真實問題在被解。下列是該題目的 application landscape 與當前主流方法。

### 應用場景

| 領域 | item | bin | dynamic 性質 |
|---|---|---|---|
| **FPGA 動態部分重組** | 計算任務的矩形區塊 | FPGA 2D 邏輯閘陣列 | 任務 runtime 進來執行、結束釋放 |
| **GPU / ML 排程** | (記憶體 × 時間) 需求 | GPU 記憶體 × 時間片 | job 提交與釋放 |
| **資料中心 2D 資源配置** | (CPU × 連續時段) / (頻寬 × 時段) | 資源池 | service / VM 啟動與終止 |
| **視訊會議 UI 切版** | 參與者矩形視窗 | 螢幕版面 | 人加入 / 離開 |
| **廣告版位排程** | 廣告（尺寸 + 上下檔時間）| 網頁 / 看板 | 活動上下檔 |
| **倉儲樓地板 / 棧板配置** | 貨物 2D 足跡 | 倉庫地板 | 進貨 / 出貨 |
| **rolling-horizon 切割排程** | 訂單矩形 | 鋼板 / 布料 | 訂單滾動到達、有些取消 |

學術上最活躍：**FPGA 動態重組**（embedded / hardware 圈，文獻最厚）與 **GPU/ML 排程**（systems 圈，最當代）。

### 主流方法（四個家族）

**家族 1：Online Placement Heuristics**（從 static 2D BP 改編）
- Bottom-Left-Fill (BLF)
- Shelf-based: Next-Fit Shelf / First-Fit Shelf / FFDH-online
- Skyline / Contour 邊界維護
- + departure 時釋放空間、更新資料結構

**家族 2：Empty Space Maintenance**（資料結構派，FPGA 圈主流）
- Empty Rectangle Lists (ERL)
- KAMER (Keep All Maximum Empty Rectangles)
- Skyline 維護
- 研究貢獻常落在「新資料結構」或「碎片化抑制策略」
- **視覺化在這派天生有切角**（看 ERL 怎麼分裂、合併）

**家族 3：Compaction / Repacking**
- 累積到碎片化指標就觸發 compaction
- Trade-off：搬遷成本 vs 碎片回收效益（GPU/ML 對應 migration overhead vs utilization）

**家族 4：Learning-Augmented / RL-based**（當代）
- 預測未來到達（learning-augmented framework，2018 後）
- RL placement policy（2020 後）
- 系統圈會議：NeurIPS / MLSys / ATC

### 文獻裂縫（你的 gap 落在哪）

1. **OR 理論派**主做 1D dynamic 的競爭比證明，**2D dynamic 理論結果稀少**
2. **Systems 實作派**（FPGA / GPU）有大量 ad-hoc heuristic，**少跟 OR 理論對話**
3. **視覺化驅動的經驗研究幾乎不存在** — 沒人系統性視覺化「不同 heuristic 在不同 workload 下產生的碎片化模式如何不同」

### 最務實的碩論切角

選一個應用場景（**建議 FPGA dynamic placement** — 文獻最厚最容易站住腳），用視覺化系統性比較 **家族 1 + 家族 2** 的方法在不同 workload 下的**碎片化失效模式**，針對觀察到的失效模式提出**小幅 heuristic 改良**。

優點：
- 不用發明全新理論
- 視覺化作為「**觀察工具**」而非僅是 demo（對應老師 2026-04-27 提示「視覺化看出數字看不到的東西」）
- heuristic 改良 + 評估即可作為碩論貢獻

### 待驗證

- 找 1–2 篇 FPGA dynamic placement 近年 survey
- 看 Christensen 2017 多維 BP survey 的 dynamic 章節
- 看 GPU scheduling 圈近 3 年（NSDI / OSDI / MLSys）的 2D dynamic 相關 paper

---

## 補充來源（比 Coffman 2013 更新或互補）

- **Christensen, Khan, Pokutta, Tetali (2017)** — *Approximation and online algorithms for multidimensional bin packing: A survey*
- **Wäscher, Haußner, Schumann (2007)** — *An improved typology of cutting and packing problems*（EJOR）
- **Mitzenmacher, Vassilvitskii (CACM 2022)** — *Algorithms with predictions*
- **OR-Library (Beasley)** — benchmark instances
- **ESICUP** — 2D packing benchmark

---

## Coffman 分類軸總表（用來定位變體）

| 軸 | 主要變體 |
|---|---|
| 時序資訊 | Offline / Online / Dynamic（有 departure）/ Stochastic / Learning-augmented |
| 空間限制 | Bounded space online（只能開 k 個 bin）/ Unbounded |
| 維度 | 1D / 2D 矩形 / 2D irregular / 3D / Vector（多資源）|
| bin 結構 | Fixed-size / Variable-sized / Bin Covering（對偶）|
| item 限制 | Cardinality / Class-constrained / Conflict graph / Fragmentable / With Rejection |
| 目標函數 | Min bins / Max value / Min makespan / Robust |

---

## 資料取得評估

| 候選 | 真實資料 | 合成資料 | 評等 |
|---|---|---|---|
| A. Dynamic 2D Rectangle BP | Hopper-Turton (2001) / Berkey-Wang (1987) 矩形 instance 自加 arrival/departure 標籤；Cloud VM trace（Google / Azure）作為 abstract reference | 隨機矩形 + Poisson arrival + duration 分布 | ★★★★★ |
| B. 2D Strip Packing | Hopper-Turton (2001), Berkey-Wang (1987), Bortfeldt 等公開 benchmark | random rectangle | ★★★★★ |
| C. Online BP with Predictions | 同 A 的 cloud trace，但要自訓預測模型或借簡單 baseline（移動平均、ARIMA）| 合成 + 人工注入預測誤差 | ★★★☆☆ |
| D. KV-cache Fragmentation Visual Atlas | BurstGPT、Mooncake trace、Azure LLM Inference trace 公開可下載 | 合成 request stream（Poisson arrival + 不同長度分布 + 取消率）| ★★★★★ |

---

## 研究缺口與碩論貢獻可能性

### A. Dynamic 2D Rectangle BP — 軸組合稀疏，gap 不薄
- Dynamic 1D 已被做爛，但 **Dynamic × 2D 矩形** 組合文獻意外稀少
- 可走角度：
  1. 套既有 2D 矩形 benchmark + 注入 arrival/departure，做經驗研究 + 視覺化 reveal failure mode + 設計改良 heuristic（最務實的碩論結構）
  2. 多維 dynamic（vector dynamic BP，cloud workload）— 與 A 同源但更應用
  3. Dynamic 2D + Predictions 交叉（A 與 C 結合）
- **碩論貢獻可達性：★★★★** — **軸組合稀疏 + 視覺化文獻空白**雙重保險

### B. 2D Strip Packing — 最成熟，gap 最薄
- 1980s 起被研究到爛，基本啟發式都有人做
- 可走角度（須往邊角推）：
  1. Online 2D strip packing 加旋轉
  2. 2D strip packing with predictions
  3. 視覺化教材本身（**不是研究貢獻**）
- **碩論貢獻可達性：★★** — 純做「並列比較視覺化」只能當 Special Topic 學習用，碩論需推到 online + rotation 或 learning-augmented，等於回到 A 或 C 的難度
- **警告**：B 是最快有 demo、但研究天花板最低的選項

### C. Online BP with Predictions — 最有 gap，最難進場
- 2018 才被 framework 化（Lykouris-Vassilvitskii），對 BP 的應用是 2021 後
- 2D、3D、dynamic、vector 各種與 predictions 的結合都還沒被做透
- **碩論貢獻可達性：★★★★★** — 前提是能跨過閱讀門檻
- **警告**：需先吃下 learning-augmented framework，入門曲線比 A 陡

---

## 兩階段策略（Special Topic vs 碩論長線）

對應老師 2026-05-04 meeting 提示：「就算這不是未來題目，也會給未來方向」。

> 注意：候選 A 鎖定 2D 矩形後，與 B 共用相當多的 placement 啟發式（NFDH / FFDH / BLF），路線 1 的學習轉移更順暢。

### 路線 1：分兩段（低風險）
- **Special Topic（6/8 demo）**：候選 **B（2D Strip Packing 啟發式並列）** 當練功題
  - 風險最低，一週可出 demo
  - 一個月內驗證視覺化工作流程，建立 2D placement 肌肉記憶
- **碩論長線**：收斂至 **A（Dynamic 2D Rectangle BP）**
  - B 累積的 placement 程式碼可直接搬到 A，補上 dynamic 時間軸即可

### 路線 2：直接選 A（中風險、較高效率）
- Special Topic 與碩論同題 = **A（Dynamic 2D Rectangle BP）**
- baseline 1.5 週可生（2D BLF + 合成 arrival/departure）
- 剩兩週半：視覺化 + 在 Hopper-Turton 改造資料上跑 + 找一個小 heuristic 改良

### 不推薦
- **直接選 B 當碩論題目** — 視覺化好做、論文難寫
- **直接上 3D Dynamic BP** — 一個月內 rendering 工作會吃掉研究時間，先 2D 站穩再擴展

---

## Special Topic 終點圖像（2026-05-11，探索中尚未鎖定）

> 對應 CLAUDE.md to-do #1「想像終點」。本節記錄 2026-05-11 對話中對 demo 螢幕呈現的初步收斂，**尚未定案**，三個「仍待決定」可能改變整體架構。

### 初步四軸選擇

| 軸 | 選擇 |
|---|---|
| Visual | 單一 canvas（一個 bin、放大看細節） |
| Pace | 時間軸 scrubber（可前後拖、定格） |
| Reveal | 單一演算法深度剖析（把 baseline 的 failure mode 拆成可命名子類） |
| Punchline | 反直覺發現型（結尾留一句「跟你以為的不一樣」） |

整體取向：**深 ＞ 廣** — 不做演算法 PK，做單一演算法解剖學。

### 內在張力：反直覺基準的三種選擇

「單一演算法 + 反直覺」需要一個「你以為」的對照基準，否則反直覺感無處生根。三個候選基準：

1. **教科書 ratio 預測 vs 實際 fragmentation 結構** — 文獻 worst-case 構造的世界 ≠ 真實 workload 的世界。「ratio 對的，但它描述的不是你身在的那個世界」。最學術。
2. **靜態分析 vs 動態行為** — 同一演算法在 static 下失敗模式 A 主導，加入 departure 後翻轉成 B（且 B 在 static 文獻沒被命名）。**與 candidate A 路線一致。**
3. **視覺直覺 vs fragmentation 指標** — 整齊 bin 其實藏致命洞。最戲劇但學術深度最薄。

**傾向 1 或 2，其中 2 與既有 candidate A 嵌合最自然。**

### 終點圖像草稿

> Special Topic 報告最後一張 demo slide。

- **畫面**：2D bin canvas 主視覺 + 底下時間軸 scrubber（0 → T）。bin 內彩色矩形 + 灰色空洞，空洞依 failure mode 類別標註（"departure scar" / "shelf-edge sliver" / "cluster void" ...）
- **互動**：拖 scrubber — t = 30s（乾淨）→ 90s（第一批 scar 出現）→ 180s（scar 累積成 canyon）→ 240s（canyon 旁 item 進不來，演算法被迫遠處塞 — **失敗模式 B 誕生時刻**）
- **側邊欄**：failure mode taxonomy 表 + 每類累積數量曲線
- **觀眾離開時記住的一句**：「靜態分析訓練我們找的失敗模式，跟動態場景真正會出現的失敗模式不是同一類東西。」

### 這份草稿鎖定的軸

| 軸 | 鎖定值 | 原因 |
|---|---|---|
| 維度 | 2D | 單一 canvas 要看細節 → 3D 會遮擋 |
| 時序 | Dynamic | scrubber 要看結構演化 → 必須有 departure |
| 容量 | 聚焦單一 bin | Visual 軸選了單一 canvas（實作可能 unbounded，但 demo 只展示先填的那個）|
| 目標 | **不是 min bins**，而是 characterize failure modes | 偏離傳統 BP 目標函數，貢獻形態因此改變 |
| 演算法 | 單一（待決定）| Reveal 軸選了深度剖析 |
| 路線定位 | 靠近 candidate A，但研究重心從「heuristic 改良」→「failure mode taxonomy」| Punchline 形態決定 |

### 仍待決定（三項）

1. **挑哪個 baseline 深剖**：BLF（2D placement 經典）/ FF（最有 textbook reputation 可顛覆）/ FFDH（2D shelf 經典）
2. **反直覺基準型**：上述 1（ratio vs 結構）vs 2（static vs dynamic）
3. **failure mode 命名方法**：人工觀察分類 / 量化指標自動分群（空洞 aspect ratio + 鄰接 item 來源 + 累積壽命）

### 注意事項

- 此取向是 **HCI ＞ 演算法**，論文貢獻會落在 failure mode taxonomy 而非新 heuristic
- 6/8 Special Topic 用此架構可行（一個月內可生 baseline + scrubber + 初步 taxonomy）
- 擴成碩論需後續加上：根據 taxonomy 對某類 failure 提出 heuristic 改良（≒ candidate A 後半段）
- 若反直覺基準選 1（ratio vs 結構），則路線會偏離 candidate A，獨立為新方向

---

## 決定欄位（2026-05-12 拍板）

- **6/8 Special Topic 採用**：候選 A（Dynamic 2D Rectangle BP）+ **abstract framing**（不綁特定場域；用 Hopper-Turton / Berkey-Wang 矩形 benchmark + 合成 arrival/departure）
  - 程式碼路線優先實作；narrative 走 A 原版（heuristic 退化比較）vs E 變體（failure mode taxonomy）5/31 前再決定（前 3 週實作共用）
- **碩論長線採用**：未定。A 為基礎，可延伸至 GPU memory / Cloud VM / KV-cache 等場域；場域選擇延後至碩論階段，依產學連結或興趣決定
- **決定原因**：
  - A 在 5 角度打分（Baseline 可實作性 / 問題鋒利度 / 報告呈現力 / 風險可控性 / 方向不相左）總分 22/25，最高且無顯著弱項
  - Abstract framing 把場域選擇延後——場域是一次性難回頭的決定，學習投資沉重，Special Topic 階段不該綁死
  - FPGA DPR 雖文獻最厚，但 gap 小且領域 2020 後退潮，只當文獻背景知識，不當研究場域
  - 詳細打分與框架推導見 `memory/research-decisions.md` 2026-05-12「收斂結論」
