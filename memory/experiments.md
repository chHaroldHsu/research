# 實驗紀錄

> 紀錄實作過程、踩過的雷、技術細節、baseline 結果、資料來源。
> 格式：`## YYYY-MM-DD` 為段落標題，最新日期置頂。

---

## 2026-05-18

### 實驗 setup 慣例

- **Bin 預設**：50×50（足夠看出 mode，跑得快）
- **n_items 預設**：200（demo） / 500（之後 H×W scan）
- **seed 預設**：42（demo）；factorial scan 會跨多個 seed 取統計
- **Heuristic 目前可用**：BLF（暴力搜尋，y outer / x inner = bottom-left-fill）
- **時間單位**：整數 tick；同 tick 多事件由 simulator 處理（departure 先於 arrival）

### Workload 模型（`dyn2dbp/workloads/synthetic.py`）

6 個 knob：

| 參數 | 模型 | 文獻 / 直覺依據 |
|---|---|---|
| `arrival_rate` λ | Poisson process，inter-arrival ~ Exp(1/λ) | 排隊論標準、Powers 2023 confirmed 真實 allocator workload |
| `size_w_range` / `size_h_range` | 均勻分布 [min, max] | Hopper-Turton 1999 spirit（item 小於 bin） |
| `lifetime_dist` | exponential / pareto / uniform | exponential 對照組；pareto α=1.5 真實重尾；uniform 控制組 |
| `mean_lifetime` | distribution 平均值參數 | 直覺：短壽 + 高 arrival → Sliver；長壽 + 低 arrival → Boundary Lockout |
| `n_items` | 整數 | 500–1000 通常足以讓 mode 反覆出現 |
| `seed` | numpy.random Generator | reproducibility 必備 |

### 5 個 preset 的設定 + BLF 結果（n=200, seed=42, 50×50 bin）

| Preset | arrival_rate | size range | lifetime_dist | mean_lifetime | Peak PE | Peak 時間 | Discard 率 | 假設 mode |
|---|---|---|---|---|---|---|---|---|
| `light_departure` | 0.2 | (3, 15) | exponential | 100 | 74.0% | t=964 | 10.5% | Boundary Lockout |
| `heavy_departure` | 1.0 | (3, 15) | exponential | 20 | 74.2% | t=53 | 9.0% | Sliver / Inland Island |
| `mixed_lifetime` | 0.5 | (3, 15) | pareto α=1.5 | 30 | 68.0% | t=157 | 2.0% | Inland Island |
| `small_items` | 0.8 | (2, 6) | exponential | 30 | 20.9% | t=144 | 0% | Staircase Skyline |
| `large_items` | 0.3 | (10, 25) | exponential | 30 | 79.0% | t=93 | 46.5% | Inland Island（大洞） |

**Peak occupancy（峰值占用率）= 整段模擬中 PE 最高的瞬間**——目前 demo 只存這張，未來要補時序 PE 曲線 + 多時間點 panel。

### 已踩的雷（lessons learned）

1. **Peak snapshot bug（已修）**：Simulator 跑完所有事件後 bin 全空（所有 item 都離開），原本 demo 存 final state 全是空白圖。修法：新增 `peak_occupancy_snapshot()` helper + `render_grid()`（從 numpy snapshot 直接畫，不依賴 live bin）。教訓：**動態實驗不能存 "final" state，要存 "peak" 或 mid-run 快照**

2. **venv shebang lock-in（已修）**：把 `code/` 整個目錄移位後 `.venv/bin/pytest` 的 shebang 還指向舊絕對路徑，導致 spawn 失敗。修法：`rm -rf .venv && uv sync` 重建。教訓：venv 不可攜，移動專案後一定重建

3. **package import path**：用 `package = false` 的 uv 專案需要 `pyproject.toml` 設 `pythonpath = ["."]` 才能讓 pytest 找到套件；scripts 透過 `sys.path.insert(0, str(Path(__file__).parent.parent))` bootstrap

### PE（Packing Efficiency 裝填效率）定義與用法

```
PE = 已占用 cell 數 / bin 總 cell 數
```

**三種 PE 要分清楚**：
- **Instantaneous PE 瞬時**：某時間點 t 的占用率（單一 snapshot 就是這個）
- **Time-averaged PE 時間平均**：整段模擬的平均占用率
- **Peak PE 峰值**：整段模擬中的最大瞬時 PE（目前 demo 圖就是這個）

**警示**：PE 不能單獨判定 heuristic 好壞——`large_items` 79% peak PE 看起來最高，但 discard 46.5%，其實是「能放的都放了、放不下的全丟」。**PE 必須跟 discard rate 一起看**。

### 變體 E 不單獨用 PE 立論

Deep-Pack 2019 / Hopper-Turton 1999 都用 final PE 比較 heuristic——這條路被占了。E 的 contribution 不在 PE 數字，而在 **mode signature + mitigation 對照表**。PE 只是基線統計值。

### 資料來源

- 文獻 PDF 在 `paper/`（已從 git 排除）：Coffman survey、Deep-Pack 2019
- 待下載：Burcea 2014 thesis、Wei 2011 IJCAI、Powers 2023 ISMM、Christensen 2017 survey

---

## 2026-05-12

- 尚未開始實作；待選題定下後啟動 baseline 實驗
