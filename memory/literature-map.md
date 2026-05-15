# Literature Map — Dynamic 2D Bin Packing

> 文獻掃描中心檔案：方法家族、關鍵字、必讀 survey、第一輪查詢、操作指引。
> 寫入時：在「已掃描清單」最上方新增該篇條目；若家族 / 關鍵字結構需更動，在頂端加 `## YYYY-MM-DD 修訂` 段落說明。

---

## 必讀 survey（從這 3 篇開始）

| # | 文獻 | 為什麼讀 |
|---|---|---|
| 1 | **Christensen, Khan, Pokutta, Tetali (2017)** *Approximation and online algorithms for multidimensional bin packing: A survey* | 唯一覆蓋 multi-dim + dynamic 的近代 survey，**最重要的一篇** |
| 2 | **Lodi, Martello, Vigo (2002)** *Recent advances on two-dimensional bin packing problems* | 2D BP placement heuristic 的入門地圖 |
| 3 | **Coffman, Csirik, Galambos, Martello, Vigo (2013)** *Bin Packing Approximation Algorithms* | BP 全領域標準參考，當字典查 |

策略：survey 倒著找——它們的引用網會把所有奠基論文打進候選清單。

---

## 方法家族（5 個主流派系）

| 家族 | 代表方法 | 哪個社群 | 代表文獻 |
|---|---|---|---|
| **1. Empty Space Maintenance** | Empty Rectangle Lists (ERL)、KAMER、Skyline、Quadtree | FPGA 圈為主 | Bazargan 2000；Steiger / Walder / Platzner 2004；Koester 2007 |
| **2. Online Placement Heuristics + departure** | BLF、Shelf-based (NF/FF/Best-Fit Shelf)、Skyline 推進 | 2D packing + FPGA | Lodi-Martello-Vigo 2002；Coffman 系列 |
| **3. Compaction / Defragmentation** | 週期 compaction、cost-aware migration、threshold-triggered | FPGA + GPU/Cloud 系統 | Koester 2007（FPGA defrag） |
| **4. Learning-Augmented / RL** | Deep RL placement、Pointer Networks、GNN encoder、with predictions | NeurIPS / MLSys | Hu 2017、Zhao 2021、Lykouris-Vassilvitskii 2018 |
| **5. Competitive Analysis / Approximation** | 競爭比證明、bounded-space variants、stochastic BP | OR 理論 | Coffman-Garey-Johnson 1983；Csirik-Woeginger 系列；Christensen 2017 survey |

**對 Special Topic 的定位**：
- 1 + 2 是 baseline 主力（會跑的就是這些）
- 3 進階（碩論階段才需要）
- 4 現代延伸（碩論可能延伸方向）
- 5 理論框架（懂概念即可，不需自證）

---

## 關鍵字（依角度分組）

### 核心
- `dynamic bin packing`
- `online bin packing with departures`
- `2D online bin packing`
- `rectangle packing online`

### FPGA 圈（最厚文獻）
- `FPGA partial reconfiguration placement`
- `FPGA dynamic task placement`
- `FPGA online placement`
- `empty rectangle FPGA`
- `KAMER FPGA`
- `FPGA defragmentation`

### 理論 / OR
- `competitive ratio bin packing`
- `multidimensional bin packing`
- `fragmentable bin packing`
- `bin packing arrival departure`

### ML / 學習增強
- `reinforcement learning bin packing`
- `neural combinatorial optimization packing`
- `bin packing with predictions`
- `learning-augmented algorithms packing`

### 現代場域（現階段不投入，留作碩論場域選擇參考）
- `GPU memory allocator fragmentation`
- `VM placement dynamic`
- `cloud resource allocation rectangle`
- `KV-cache fragmentation PagedAttention`

---

## 要 follow 的研究者 / 群組

- **Coffman**（BP 理論奠基）— 1983 dynamic BP 原始 paper + 2013 survey
- **Lodi, Martello, Vigo**（2D BP placement heuristic 經典）
- **Bazargan, Steiger, Walder, Platzner**（FPGA dynamic placement）
- **Christensen, Khan, Pokutta, Tetali**（2017 multi-dim BP survey 作者）
- **Csirik, Woeginger**（online BP 理論系列）

---

## 重點 venue（按主題濃度排序）

- **2D BP / OR**：EJOR、Operations Research、INFORMS J. Computing、Journal of Scheduling、SODA、ESA、ICALP
- **FPGA Dynamic Placement**：FPL、FPGA、FCCM、DAC、IEEE Trans. Computers、ACM TRETS
- **學習增強 / RL**：NeurIPS、ICML、ICLR、MLSys
- **現代系統應用**：OSDI、SOSP、NSDI、ATC、MLSys

---

## 第一輪 Google Scholar 查詢

直接複製貼上：

```
("dynamic bin packing" OR "online bin packing") "departure" 2D
"FPGA" "partial reconfiguration" "online placement"
"two-dimensional" "online bin packing" rectangle
"bin packing with predictions" 2D
"empty rectangle" placement FPGA
```

排序時優先 2017+ 引用網路，**從 survey 倒著找**奠基論文。

---

## 操作指引：positioning scan，不是泛掃

對每篇找到的論文，主動回答下列問題（對齊 `memory/research-decisions.md` 2026-05-12 行動 to-dos 第 1 條）：

### 通用三題
1. **它做了什麼 heuristic 比較？**
2. **它有命名／量化 failure mode 嗎？**
3. **它的 framing 是 FPGA-specific 還是 generic BP？**

### Positioning 三題（支持報告結尾 next-step claim）
1. **別人在 dynamic 2D BP 上已優化過什麼**（家族 1–4 各自最新進展）
2. **那些優化的邊界在哪**——哪些 workload / failure mode 沒處理好
3. **我預計的觀察可能落在哪個邊界外**

### H1–H5 假設驅動
對每篇 paper，標註它對 5 個假設（見 `memory/research-decisions.md`）的關係：
- **直接 claim 結論** → 該假設失效，棄
- **部分證據但未系統化** → 假設仍有效，定位為「補完零散觀察」
- **完全沒人提過** → 假設最有 value，但警覺是否「沒人在乎」

掃完後產出對照表：H1–H5 哪幾個已被覆蓋、哪幾個還空著。**該表本身會直接變成 Special Topic 報告的 Related Work 章節骨架。**

---

## 已掃描清單（持續更新）

> 格式：`- [paper-id] 作者 (年) 標題 | 家族 | 對 H1–H5 的關係 | 對 next-step 的啟示`

### 2026-05-14 快速 positioning scan（agent 驅動 ~30 分鐘）

**目的**：驗證 A（heuristic 排名重洗）與 E（failure mode taxonomy 失敗模式分類學）兩條 narrative 的差異化空間。**結論：E 強、A 中強，narrative 提前收斂至 E**（見 `research-decisions.md` 2026-05-14 段）。

**A 軌道（已被占走）**：
- Burcea (PhD thesis, Liverpool 2014) *Online Dynamic Bin Packing* | 家族 5 競爭分析 | A 部分覆蓋 | 2D/3D dynamic BP arrival+departure，**競爭比上界 2DDynamicPackUFS1 ≈ 6.785**——理論側 saturate（飽和），但不做 BLF/NFDH/FFDH 實證對照
- Wong et al. WAOA 2009 *Competitive Multi-Dimensional Dynamic Bin Packing via L-Shape* | 家族 5 | A 部分覆蓋 | 同樣 competitive analysis 路線
- Kundu & Dutta, ICRA 2019 *Deep-Pack* + arXiv 2409.09677 (2024) *Mitigating Dimensionality...* | 家族 4 RL | A 部分覆蓋 | RL 2D packing 把 BLF/Shelf 當 baseline，**但全部 no-departure**，且非 static→dynamic 對照

**E 軌道（最接近的全是 metric，不是分類學）**：
- Tabero et al. (~2006) *Perimeter quadrature-based metric for FPGA fragmentation in 2D HW multitasking* | 家族 1 + 3 | E 未覆蓋 | 給單一純量 fragmentation metric（碎片度量），**不命名 mode**
- Wei et al. IJCAI 2011 *Space Defragmentation Heuristic for 2D and 3D Bin Packing* | 家族 3 | E 未覆蓋 | 做 defrag（重整）operation（push-along-axis 沿軸推擠），**不分類失敗形狀**
- Powers et al. arXiv 2304.10862 + ISMM 2023 *Viewing Allocators as Bin Packing Solvers Demystifies Fragmentation* | 家族 1 + 5 | E 未覆蓋 | 把 DSA（動態儲存配置）對應到 2DBP，**仍走 metric 與 Spearman 相關性**（spearman correlation 史皮爾曼相關係數）

**待細讀補強**：Burcea 2014 全文、Wei 2011 IJCAI、Powers 2023——確認他們確實沒做 taxonomy。

**Survey 入口仍待讀**：Christensen-Khan-Pokutta-Tetali 2017（multi-dim BP 多維分箱裝箱 survey 綜述）、Lodi-Martello-Vigo 2002、Coffman 2013。

#### 2026-05-14 補強：arXiv 2409.09677 摘要確認

Kołodziejczyk & Kaleta (2024) *Mitigating Dimensionality in 2D Rectangle Packing Problem under Reinforcement Learning Schema* | 家族 4 RL | A 部分 / 進階 6 未覆蓋
- 解 RL 2D packing 的 **dimensionality（維度）爆炸**問題：用 UNet + PPO（Proximal Policy Optimization 近端策略最佳化）做 reduced state/action representation（降維狀態與動作表示）
- Baseline 只比 **MaxRect heuristic（最大矩形啟發式）**，**沒比 Deep-Pack**
- **無 departure（離開）、無 mode-conditioning（模式條件化）**——確認 RL 2D packing 圈仍停在「靜態 + 大 bin」子問題
- 對進階 6（mode 當 RL state feature）的影響：**沒搶到位置**，差異化空間仍空著。未來進階 6 baseline 至少要對到 vanilla DRL（Deep-Pack 風格擴 dynamic）+ dimensionality-reduced DRL（這篇風格）

#### 2026-05-14 補強：變體 E 差異化矩陣（Related Work 章節骨架）

整合 5/14 scan 的 prior work（先前研究），列出 E 的 4 個未占維度。**此表將直接作為 Special Topic 報告 Related Work 章節的骨架**。

| 維度 | Tabero 06 | Wei 11 | Powers 23 | Burcea 14 | Deep-Pack 19 | **變體 E** |
|---|---|---|---|---|---|---|
| 處理動態 (with departure) | ✅ | ❌ | ✅ | ✅ | ❌ | ✅ |
| 觀察 / 量化 fragmentation 碎片度 | ✅ 純量 | ❌（直接修）| ✅ 純量 | ❌（純理論）| ❌ | ✅ 分類 + 純量 signature |
| **命名失敗模式 (named failure modes)** | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ **空格 → E 核心** |
| **每個 mode 的 quantitative signature 量化簽章** | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ **空格** |
| **mode-targeted mitigation 模式針對性緩解** | ❌ | 通用 push | ❌ | ❌ | ❌ | ✅ **空格** |
| **跨 heuristic × workload 系統掃描** | ❌ | ❌ | 部分（Spearman）| ❌ | ❌ | ✅ **空格** |
| 視覺化呈現失敗形狀 | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |

**E 差異化的 4 句濃縮**（report 主張的骨幹）：
1. Prior work 給 scalar metric（純量指標）；E 給 categorical taxonomy（類別分類學）——答的問題從「有多碎？」變成「碎成什麼形狀、為什麼？」
2. Prior work 把 fragmentation 當症狀；E 分解成不同 mechanism（機制）——Sliver Strip / Inland Island / Boundary Lockout / Staircase Skyline 各有不同形成機制
3. Prior work 給通用 mitigation；E 給 mode-targeted mitigation——Sliver 用 reservation（預留）、Inland Island 用 compaction（壓縮）、Boundary Lockout 用 long-lived item 預先側放
4. Prior work 多在單一 heuristic / workload 上觀察；E 做 cross 系統掃描，產出 heuristic × workload → mode 對應表

**口試「so what?」回答模板**：
> Prior work（Tabero 06 / Wei 11 / Powers 23）已證明 dynamic 2D BP 會 fragment 並提出純量 metric 與通用 defrag operator（重整算子），但**沒有解釋失敗的內在結構**——同樣 metric 值可對應不同失敗形狀，需要不同 mitigation。E 補上 named modes + quantitative signatures + mode-targeted mitigation matrix，把「dynamic BP 的優化」從「降一個總數」變成「針對特定 mode attack（攻擊）」，並為後續 RL agent 提供 mode label 作為 inductive bias（歸納偏置，即進階 6 的伏筆）。
