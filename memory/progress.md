# 進度紀錄

> 紀錄階段性進展、完成的里程碑、卡關狀況。
> 格式：`## YYYY-MM-DD` 為段落標題，最新日期置頂。

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
- **楊老師 sanity check**：還沒約
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
