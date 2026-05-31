# 進度紀錄

> 紀錄階段性進展、完成的里程碑、卡關狀況。
> 格式：`## YYYY-MM-DD` 為段落標題，最新日期置頂。

---

## 2026-05-25

### 老師 meeting 完成 + Oracle Gap 算出

**Meeting 成果**：
- 老師認可主軸方向：根據 bin 狀態動態選最佳 heuristic（棋盤比喻）
- 下一步：查找是否有相關的 existing approach（dynamic heuristic switching for BP）
- 老師也問 DRL 那篇論文的衡量指標是什麼、跟誰比較——需要回去查

**Oracle Gap 實測**：Gap = 0%，BLF 在 150/150 run 全勝。原因是 shelf 與幾何式 heuristic 不在同一等級。→ exp 2026-05-25

**新卡關**：現有 4 heuristic 集合無法支撐 dynamic switching narrative。要讓主軸成立，需擴充幾何式 heuristic（Maxrects / Skyline / Guillotine）。→ ideas 2026-05-25

**調整後的優先順序**：
1. prior work 細讀（原本就是 #1，現在多一個目標：找 dynamic heuristic switching 相關研究）
2. 擴充 heuristic 集合（讓 Oracle Gap > 0）
3. 重算 Oracle Gap → 確認 dynamic switching 有價值
4. 命名 mode + 報告

---

## 2026-05-23

### 第 4 週前置 #2–#5 一次跑完（30-seed sweep）

5/22 對話釐清「現在 model 真能說 workload 量化得出 fragmentation pattern 嗎」→ 列出 4 項前置（後加上 #1 prior work 共 5 項）。今天把 #2–#5 一次跑完：seeds 拉到 30 = 600 runs，產出 30 張 grid_view + signature 2D scatter + PCA + cluster stats。詳數據 → experiments 2026-05-23。

**主要成果**：

- 6 個量化 mode 在 30-seed 重複下穩定（≥ 60% dominant，多數 100%）：Brick-wall、Horizontal-stripe、Top-sliver、Sparse-BLF、Item-too-tall、Sparse-stripe
- **2 個原始候選退場**：Inland Island（signature 重疊、視覺無區別）、Shelf abandonment（NFS 與 FFS/BFS 同 mode 標籤）
- Signature 改為 **2D（peak PE + discard）+ mean/peak 輔助**，F@peak 完全降級（σ 對 BLF 翻倍 seed-dependent）
- E 變體貢獻邊界釐清：**Brick-wall / Horizontal-stripe 是 heuristic-family baseline；研究貢獻在 4 個 workload-induced mode**

**意外發現**：

- light_dep 與 heavy_dep 在 peak signature 上等價（d/σ ≤ 0.16）→ 兩個 preset 等同名字不同的同一 workload，時序維度才能分
- FFS ≡ BFS 在 4 個 metric 全部成立 → 報告可省一個 heuristic
- PCA 確認 signature space 本質低維（前 2 維 92% 變異）

**剩下卡關**：

> SUPERSEDED 2026-05-25：老師 meeting 已完成 → see progress#2026-05-25
- ~~第 4 週剩 #1 prior work（命名 mode 前必須）；楊老師 sanity check 仍未約~~
- Mode 數量 6 個 > 3 門檻，fallback 安全
> SUPERSEDED 2026-05-25：Oracle Gap 已算出 = 0%，BLF 全勝 → see experiments#2026-05-25
- ~~Oracle Gap 計算可開始：cluster 分群清楚 → mode-aware oracle 有明確選法~~

---

## 2026-05-19

### 第 3 週收尾完成（4 件一次跑完）

1. Seed sweep：`scripts/seed_sweep.py`，4 heuristic × 5 preset × 10 seeds = 200 runs。CSV 在 `code/figures/seed_sweep_raw.csv`
2. Fragmentation F + mean/peak ratio：4×5 grid_view annotation 從 2 數字擴成 4 數字（peak PE / discard / F@peak / mean/peak）
3. 時序快照 sampling：`viz/snapshot.py::sample_snapshots()` + `scripts/demo_timeseries.py`
4. 75/75 tests pass

**關鍵成果**：FFS ≈ BFS 跨 10 seed Δ ≪ σ → 報告可下「等價」結論。Mode signature 雛形：BLF F@peak 3–6，shelf 家族 F@peak 7–11，shelf 大物失敗時 mean/peak < 0.2。詳數據 → experiments 2026-05-19。

### 卡關 / 待決

- 第 4 週進前必須讀完 Burcea 2014 / Wei 2011 / Powers 2023（避免重命名 prior work mode）
> SUPERSEDED 2026-05-25：老師 meeting 已完成 → see progress#2026-05-25
- ~~楊老師 sanity check 仍未約~~

---

## 2026-05-18

### 第 1 週 deliverable 完成（5/14 開工，5/15 git push）

- 專案結構重組：所有程式相關搬入 `code/`，研究筆記層（`memory/`、`context/`、`paper/`）保持在 root
- `dyn2dbp` 套件骨架（uv + Python 3.11+，50×50 bin 預設）：
  - `core/`：`Item`、`Position`、`BinState`、event-driven `Simulator`（同 tick departure 先於 arrival 的 tie-break）
  - `heuristics/`：`PlacementStrategy` ABC + BLF 暴力搜尋實作
  - `viz/snapshot.py`：matplotlib 渲染器（by lifetime 著色）
- 18 個 pytest 全綠（BinState 9 + BLF 5 + Simulator 4）
- 端到端 demo（10 個手刻 item）跑通
- 程式碼層 git 備份至 `chHaroldHsu/research`（private repo）

### 第 2 週進行中（5/17 起）

**已完成**：
- `dyn2dbp/workloads/`：`WorkloadConfig` + `SyntheticWorkload`（Poisson arrival + 三種 lifetime 分布 exponential / pareto / uniform）
- 5 個 preset：`light_departure` / `heavy_departure` / `mixed_lifetime` / `small_items` / `large_items`
- 13 個新增測試（總計 31/31 全綠）
- Bug fix：peak snapshot 渲染（原本存 final state 都空白，因為跑完所有 departure 後 bin 全空；改成存 peak occupancy 那一張）
- 新增 `render_grid()` + `peak_occupancy_snapshot()` helper

**未完成（剩餘第 2 週工作）**：
- `metrics/`（time-series PE、discard rate、Tabero fragmentation metric 對照組）
- `viz/grid_view.py`（H × W subplot 並排）
- `viz/animation.py`（gif 動畫）

### 第一個量化證據（支持 5/14 H × W factorial 設計假設）

BLF × 5 preset（n=200, seed=42, 50×50 bin）跑出來：

| Preset | Peak PE | Discard 率 |
|---|---|---|
| `light_departure` | 74.0% | 10.5% |
| `heavy_departure` | 74.2% | 9.0% |
| `mixed_lifetime` | 68.0% | 2.0% |
| `small_items` | 20.9% | 0% |
| `large_items` | 79.0% | **46.5%** |

**意義**：同一個 BLF，5 種 workload 下 discard rate 從 0% 到 46.5%——**workload 確實大幅影響 heuristic 行為**。`heavy_departure` peak 圖（figures/demo_workload_heavy_departure_seed42.png）已能肉眼觀察到 candidate Inland Island 雛形（長壽 item 周圍有白色空隙），但**尚未量化**。

### 卡關 / 待決

- **prior work 細讀**：Burcea 2014 / Wei 2011 IJCAI / Powers 2023 全文還沒做（mode 命名前必須做）
> SUPERSEDED 2026-05-25：老師 meeting 已完成 → see progress#2026-05-25
- ~~**楊老師 sanity check**：還沒約~~
- **fallback 檢核點**：第 3 週末若 ≥ 3 個 distinct mode 找不出來，要觸發退回變體 A

---

## 2026-05-12

### 進度
- 研究階段：選題收斂 + Deep Dive 啟動
- 當前聚焦：本月內鎖定 Bin-Packing 子問題、產出視覺化原型，作為 Special Topic 報告內容
- **5/10 選題期限已逾期**

### 卡關狀況：Dynamic 2D Rect BP 選題的兩難
在「視覺化 + dynamic 2D BP baseline」路線深入思考後，意識到：
- 純理論 heuristic 改良在成熟領域幾乎無貢獻空間
- 場域變體有貢獻空間但需要 domain knowledge，獨自摸索成本高
- 視覺化只能加速直覺，不能在成熟領域生出新研究問題

思考已收斂到「兩個時間尺度分開（Special Topic vs 碩論用不同標準）」的策略框架，**但尚未對任何具體方向（包括是否將 Special Topic 重新定位為 diagnostic survey）做出決定**。

### 待辦
- 待決：是否接受 Special Topic 重新定位
- 待決：是否近期約楊老師討論變體場域選擇
- 平行可行：開始讀 5–10 篇 dynamic 2D BP 應用論文，建變體清單表
- 6 月前產出 baseline 視覺化原型
- 6/8 報告週前完成 8 成內容
