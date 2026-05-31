# 實驗紀錄

> 紀錄實作過程、踩過的雷、技術細節、baseline 結果、資料來源。
> 格式：`## YYYY-MM-DD` 為段落標題，最新日期置頂。

---

## 2026-05-25 — Oracle Gap 計算

用 seed_sweep_raw.csv（4 heuristic × 5 preset × 30 seeds = 600 runs）計算 Oracle Gap。

**方法**：
- X = single-best heuristic 的 grand mean peak PE（跨 5 workload 平均）
- Y = mode-aware oracle（每個 workload 挑最佳 heuristic）的平均 peak PE
- Gap = Y − X

**Mean peak PE per (heuristic, workload)**：

- BLF: heavy 0.7207 / large 0.8079 / light 0.7260 / mixed 0.6427 / small 0.2075
- NFS: heavy 0.3184 / large 0.4551 / light 0.3272 / mixed 0.3254 / small 0.1614
- FFS: heavy 0.4039 / large 0.4911 / light 0.4169 / mixed 0.3698 / small 0.1902
- BFS: heavy 0.4064 / large 0.4888 / light 0.4195 / mixed 0.3703 / small 0.1902

**Grand mean per heuristic（X 候選）**：BLF 0.6210 / BFS 0.3751 / FFS 0.3744 / NFS 0.3175

**Oracle picks per workload（Y 計算）**：5/5 workload 全選 BLF

**結果**：X = 0.6210, Y = 0.6210, **Gap = 0%**。BLF 在 150/150 個 run 全勝，per-seed 也無例外。

**解讀**：shelf 家族（NFS/FFS/BFS）與幾何式 BLF 不在同一等級，oracle 永遠選 BLF。現有 heuristic 集合無法支撐 dynamic switching narrative。→ ideas 2026-05-25（擴充方向）

---

## 2026-05-23 — 前置 #2–#5 一次跑完：30-seed sweep + signature cluster + intrinsic/induced 分類

對話決定 seeds 拉到 30、用同一批 600 runs 把前置 #2/#3/#4/#5 全部跑出來。產出 3 個新檔：`figures/seed_grid/grid_view_seed01..30.png`（30 張）、`figures/signature_2d.png`、`figures/signature_pca.png`、新腳本 `scripts/mode_stability_sweep.py` + `scripts/signature_analysis.py`。

### #2 重做：30 seeds 比 10 seeds 揭露什麼

主要 signature 結論不變但**有 3 個新訊號**：

- shelf 家族 peak PE 整體比 10-seed 估計低 3–4 pp（FFS light 0.454 → 0.417、heavy 0.440 → 0.404、mixed 0.427 → 0.370）。10-seed 高估了 shelf，後續報告數字以 30-seed 為準
- F@peak 在 BLF 的 σ 幾乎翻倍（light σ 1.33→2.91、heavy 2.33→3.72、large 1.74→2.48）→ F@peak 對 BLF 強烈 seed-dependent，從 signature 完全降級確認無誤
- BLF×mixed_lifetime 的 mean/peak σ 也放大（0.095→0.108）→ BLF mixed 是不穩定 cell，命名 mode 慎用

→ 修正後的工作 signature：**2D（peak PE + discard）為主**，mean/peak 為輔（標 σ），F@peak 完全降級。`figures/signature_pca.png` 確認 (peak_pe, discard, mean/peak) 三維 PCA 前 2 維捕捉 **92% 變異**——signature space 本質上是低維的，2D 就夠講故事。

### #3 Mode 視覺穩定性（30 seeds 量化檢驗）

`signature_analysis.py` 對每個 (heuristic, preset, seed) 用 signature threshold 分類，統計每個 cell 的 dominant mode 出現次數：

- BLF × light_dep → Brick-wall **24/30**（80%）
- BLF × heavy_dep → Brick-wall **25/30**（83%）
- BLF × mixed_lifetime → Brick-wall **29/30**（97%）
- BLF × small_items → Sparse-BLF **30/30**（100%）
- BLF × large_items → Top-sliver **29/30**（97%）
- NFS × {light, heavy, mixed} → Horizontal-stripe **30/30**（100%）
- NFS × small_items → Sparse-stripe **30/30**
- NFS × large_items → Item-too-tall **30/30**
- FFS × {light, heavy, mixed} → Horizontal-stripe 28–29/30
- FFS × small_items → Sparse-stripe 30/30
- FFS × large_items → Item-too-tall 28/30
- BFS：完全跟 FFS 同（見下方 cluster 分析）

**6 個量化 mode 全部 ≥ 60% 門檻通過**。但兩個原始候選**沒撐住**：

- **Inland Island 退場**：BLF × heavy_departure 跟 BLF × light_departure 在 signature 空間 d/σ = 0.16（完全 OVERLAP），無法用 signature 分離。視覺抽 4 個 seed（1, 10, 20, 30）也看不出「島」感跟普通 brick-wall 的差別。要救回需要做 grid topology（trapped void detector），目前不做
- **Shelf abandonment 不是 NFS 獨有**：NFS × {light,heavy,mixed} 跟 FFS/BFS × {light,heavy,mixed} 都被歸為 Horizontal-stripe（PE 較低但 mode 標籤一致）。NFS 的「廢棄 shelf」是 PE 較低（0.32 vs 0.41），可在 narrative 區分為「Stripe-NFS subtype（PE ~0.32）vs Stripe-FFS/BFS subtype（PE ~0.41）」，但不算獨立 mode

### #4 Cluster 分析（signature 空間分離度）

PCA 前 2 維 92% 變異；2D 圖（peak_pe × discard）肉眼可見 **7 個視覺集群**：

- BLF×{light,heavy}（PE 0.72, discard 0.07）一群
- BLF×mixed（PE 0.64, discard 0）一群
- BLF×small（PE 0.21, discard 0）一群
- BLF×large（PE 0.81, discard 0.42）孤立群
- Shelf 家族 ×{light,heavy,mixed}（PE 0.32–0.42, discard 0.85–0.90）一大群（重疊）
- Shelf 家族 ×small（PE 0.16–0.19, discard 0.34–0.59）一群
- Shelf 家族 ×large（PE 0.45–0.49, discard 0.96–0.97）一群

**Nearest-cell distance / σ ratio < 1.5 視為 OVERLAP**，發現 12 對 overlap pairs。其中 7 對是 FFS↔BFS 同 preset 配對（d/σ < 0.05，完全重合），剩下 5 對：

- BLF light ↔ BLF heavy（d/σ = 0.16）→ **light_dep 跟 heavy_dep 在 peak signature 上無法分離**。這是新發現，意義：兩個 workload 在 peak 時長一樣，差異只在 transient（時序）
- NFS light ↔ NFS heavy（d/σ = 0.08）→ 同上
- NFS mixed 接近 FFS mixed（d/σ = 0.51）→ shelf 家族在 mixed 上比在 light/heavy 上更接近
- NFS large 接近 BFS large（d/σ = 0.27）→ shelf 家族在 large_items 上全部 collapse

→ **light_dep ≡ heavy_dep 在 peak signature 上**，等同當前是「兩個名字的同一個 workload」。下游 narrative 可選：合併成一個 preset、或用時序差異補強區別

### #5 Heuristic-intrinsic vs workload-induced（stable_threshold = 60% in cell）

- **Heuristic-intrinsic**（同一個 heuristic 跨多個 preset 都出現的 mode）
  - Brick-wall：BLF × {light, heavy, mixed} → 3/5 preset
  - Horizontal-stripe：NFS/FFS/BFS 各 × {light, heavy, mixed} → 3/5 preset 每個 heuristic
- **Workload-induced**（綁定特定 preset 才出現的 mode）
  - Top-sliver：BLF × large_items 獨有 → 1/5
  - Sparse-BLF：BLF × small_items 獨有 → 1/5
  - Item-too-tall：shelf × large_items 獨有 → 1/5
  - Sparse-stripe：shelf × small_items 獨有 → 1/5

→ 研究真正貢獻在 **4 個 workload-induced mode**。Brick-wall 與 Horizontal-stripe 降級為「heuristic-family baseline behavior」，從「貢獻」變「背景」。

### 對 narrative 的影響

報告 punchline 候選句修正：

- 舊：「workload 變化讓 heuristic 退化出 6 種 fragmentation mode」
- 新：「Heuristic family 主導 2 個 baseline mode（brick-wall vs stripe）；workload **進一步分離**出 4 個邊角 mode（sparse / sliver / too-tall），所有 mode 在 30-seed 重複下 signature 穩定（≥ 60% dominant，多數 100%）」

E 變體貢獻邊界比原本想的窄但**清楚**：4 個 workload-induced mode 是新的、可量化、視覺可辨。Mode 數量還在 ≥ 3 門檻之上，fallback 沒被觸發。

> SUPERSEDED 2026-05-25：Oracle Gap 已算出 = 0%（BLF 全勝），非「可觀 gap」→ see experiments#2026-05-25
~~Oracle Gap 計算可開始：peak signature 分群清楚 → mode-aware oracle 知道在 (heuristic, preset) 配對下選誰，比 single-best 跨 5 preset 平均應有可觀 gap。~~

### 副產物 finding（值得記在 ideas）

- light_departure 與 heavy_departure 兩個 preset 在 peak signature 上等價 → 證明「peak 信號丟掉時序差異」是 dynamic BP 的特性，不是 bug。時序 signature（如 turnover rate at peak）是補回時間維度的方向
- FFS ≡ BFS 在 4 個 metric 全部成立（peak PE、mean/peak、F@peak、peak F），不只是 peak PE。報告可寫「FFS 與 BFS 在當前參數區內全 signature 等價」，省一個 heuristic
- BLF mixed 是 BLF 最不穩定的 cell（peak PE σ 0.049 / mean/peak σ 0.108）。mixed_lifetime 對 BLF 有獨特挑戰，可能與長壽 item 的 placement 衝突有關——未來解釋

---

## 2026-05-22 — 前置 #2：4 元件 signature 跨 10 seed 完整重跑

第 4 週前置 #1 的副產物：原以為 F@peak / mean/peak 只有 n=1，重看 `seed_sweep.py` 才發現 schema 早有這 2 欄、200 rows 跨 10 seeds 早就在了，只是 5/19 experiments memo 沒寫出來。重跑 sweep 確認，並補完所有 4 元件的跨 seed mean ± std。

### mean/peak PE ratio

- BLF：light_dep 0.567±0.035 / heavy 0.563±0.023 / **mixed 0.394±0.095** / small 0.499±0.033 / large 0.587±0.035
- NFS：light 0.350±0.098 / heavy 0.353±0.097 / mixed 0.223±0.089 / small 0.392±0.065 / **large 0.501±0.217**
- FFS：light 0.293±0.097 / heavy 0.299±0.099 / mixed 0.218±0.138 / small 0.430±0.045 / large 0.396±0.132
- BFS：light 0.284±0.103 / heavy 0.289±0.103 / mixed 0.212±0.139 / small 0.419±0.049 / large 0.396±0.132
- mixed_lifetime 全 heuristic σ 顯著放大 → 該 cell 不穩定，命名 mode 要慎用此指標
- shelf 家族 large_items 上 σ 巨大（NFS 0.501±0.217）→ NaN/edge-case 風險

### F at peak-PE time（=「F@peak」實際讀取的欄位）

- BLF：light 4.69±1.33 / heavy 6.48±2.33 / mixed 4.57±2.67 / **small 1.69±0.32** / large 3.88±1.74
- NFS：light 4.38±1.20 / heavy 4.48±1.39 / mixed 4.08±1.01 / small 6.48±1.08 / large 3.60±1.01
- FFS：light 6.03±2.09 / heavy 5.89±2.15 / mixed 4.59±2.12 / small 5.80±1.56 / large 4.04±1.52
- BFS：light 6.29±2.01 / heavy 6.27±2.01 / mixed 5.15±1.81 / small 5.88±1.63 / large 4.04±1.52

### Peak fragmentation F（整段 run 最大 F，**不**等於 F@peak PE）

- BLF：light 16.10±3.03 / heavy 15.22±2.92 / mixed 10.84±1.57 / small 3.63±0.48 / large 9.56±1.67
- NFS：light 4.99±1.09 / heavy 5.02±1.07 / mixed 5.04±1.29 / small 6.71±0.91 / large 3.91±0.97
- FFS：light 7.86±1.96 / heavy 7.77±1.90 / mixed 6.83±1.68 / small 7.26±0.64 / large 4.61±1.18
- BFS：light 8.05±2.13 / heavy 7.88±1.88 / mixed 6.69±1.50 / small 7.44±0.81 / large 4.61±1.18

### 關鍵發現：signature 雛形需修

5/19 寫的「BLF F@peak 3–6 / shelf F@peak 7–11」**錯了兩件事**：

- 那 7–11 是 `peak_f`（整段 run 最大 F），不是 `f_at_peak_pe`（peak PE 那刻的 F）。當時讀錯欄位
- 用 `f_at_peak_pe` 跨 10 seed 重看，BLF 跟 shelf 在非 small/large workload 都落 4–6 區、**大量重疊**，F 不是有效分離器

剩下站得住的分離器（按強度排）：

1. **peak PE**：BLF 63–82%、shelf 17–49%——強分離
2. **discard rate**：BLF 0–7%、shelf 33–97%——強分離（small_items 例外，BLF/shelf 都 0–60%）
3. **mean/peak ratio**：BLF 0.39–0.59、shelf 0.21–0.50——弱分離，BLF mixed cell 與 shelf large cell 重疊
4. **F at peak-PE time**：4–6 區大量重疊——**不是分離器**

→ 5/19 signature 表已加 SUPERSEDED marker。命名 mode 時主要靠 peak PE + discard 切大 mode，mean/peak 當輔助、F@peak 從 signature 候選**降級**或改用 peak_f（但 peak_f 也要重新檢驗它的物理意義）。

### 對前置 #3–#5 的影響

- 前置 #3（mode 視覺穩定性）不變，照樣 loop 10 seeds 畫圖
- 前置 #4（signature 空間分離）現在更該做：peak PE + discard 二維平面就可能足夠看 cluster，F@peak 就別塞了
- 前置 #5（heuristic-intrinsic vs workload-induced）不變

### 副產物 finding

- BLF peak F（整段最大 F）在 light/heavy/mixed 達 10–16，**比 shelf 家族（5–8）高一截**。直觀違反「BLF 越擺越緊」的預期——可能是 BLF 中途有大量小縫產生但後續被填掉、或 departure 造成 transient sliver。值得留作未來解釋
- FFS ≈ BFS 重合在 mean/peak、F@peak、peak F 三個指標**也成立**（差 ≤ 0.03 / ≤ 0.3 / ≤ 0.3）。5/19 只看 peak PE，現在四指標一致。報告可寫「FFS 與 BFS 在當前參數區內全 signature 等價」

---

## 2026-05-19 — 第 3 週收尾：seed sweep + 三個 signature 元件套到 4×5

第 3 週的 4 件 cleanup 一次跑完：seed sweep / fragmentation 套 annotation / mean/peak PE ratio 補完 / 時序快照 sampling。

### 1) Seed sweep (n=200, seeds=1–10, bin=50×50)

`scripts/seed_sweep.py` 跑 4 heuristic × 5 preset × 10 seeds = 200 runs，raw 結果 `code/figures/seed_sweep_raw.csv`。每格輸出 mean ± std。

**FFS ≈ BFS 驗證 — 跨 10 seed 全部 Δ ≪ σ，重合確認為真現象不是 seed=42 artefact**：

| Preset | FFS peak PE | BFS peak PE | Δ |
|---|---|---|---|
| light_departure | 0.454 ± 0.085 | 0.458 ± 0.083 | 0.003 |
| heavy_departure | 0.440 ± 0.087 | 0.443 ± 0.082 | 0.003 |
| mixed_lifetime | 0.427 ± 0.082 | 0.429 ± 0.083 | 0.002 |
| small_items | 0.196 ± 0.025 | 0.196 ± 0.025 | 0.000 |
| large_items | 0.489 ± 0.110 | 0.489 ± 0.110 | 0.000 |

→ 報告可寫「在此參數區內 FFS 與 BFS 行為等價」。**碩論若擴 bin/item 比，要重驗。**

**順帶踩雷**：seed=42 對 shelf 家族是低端 outlier。seed=42 下 NFS peak PE = 24%，跨 10 seed mean = 33%；FFS/BFS seed=42 = 35%，跨 seed mean = 45%。BLF 反而穩（74% → 72.7 ± 3.7%）。原本 5/18 晚的 4×5 表低估了 shelf 家族的典型 packing 能力——但 discard 數字穩，所以 mode 判讀不變。

### 2) Fragmentation F 套到 4×5 annotation

`scripts/demo_grid_view.py` 的 annotation 從「peak PE / discard」擴成「peak PE / discard / F@peak / mean/peak ratio」四數字。seed=42 圖（`code/figures/grid_view_seed42.png`）已更新。

**Mode signature 雛形浮現**：

> SUPERSEDED 2026-05-22：F@peak 欄位讀錯（讀成 peak_f 而非 f_at_peak_pe），且全表為 seed=42 單次觀察。跨 10 seed 重檢後 F@peak 不是分離器、mean/peak 為弱分離 → see experiments.md#2026-05-22

| Mode 候選 | peak PE | discard | F@peak | mean/peak |
|---|---|---|---|---|
| BLF brick-wall | 70%+ | <15%（小 item 0%；大 item 46%） | 3–6 | 0.55–0.60 |
| Shelf horizontal stripe | 30–35% | 84–88% | **7–11**（最高） | 0.17–0.34 |
| Shelf large-item failure | 34%（容不下） | 96% | 2.1（empty） | **0.13** |

→ shelf 家族的高 F@peak（7–11 vs BLF 3–6）是量化條紋空白的好訊號。**mean/peak ratio < 0.2** 是 catastrophic discard 的早期警示（bin 只在前期短暫填滿，後面全 discard）。

### 3) 時序快照 sampling（多框架）

新增 `dyn2dbp/viz/snapshot.py::sample_snapshots(snapshots, k, include_peak=True)`：等間距挑 k 個時間點，peak occupancy 強制塞入。`scripts/demo_timeseries.py` 渲染 4 heuristic × k frame 的時間演化圖（單 preset）。

**踩雷**：原本 sampling 跨整個 run，但 arrival 結束後 bin 純 drainage，後面 frame 全 PE=0%。改成 sample 範圍限制在 `[first_event, last_arrival_t]` 的 arrival window 內。

產出：`figures/timeseries_heavy_departure_seed42.png` / `figures/timeseries_large_items_seed42.png`。第 4 週命名 mode 用。

### 第 3 週收尾狀態

- ✅ 4×5 factorial（5/18 晚）
- ✅ seed sweep ≥ 10
- ✅ fragmentation 套 annotation
- ✅ mean/peak PE ratio 全 4×5
- ✅ 時序快照 sampling 基礎建設
- 75/75 tests pass

→ 進第 4 週：命名 mode → mode signature → mitigation 對照表。**命名前必須**先讀 Burcea 2014 / Wei 2011 / Powers 2023 避免重命名 prior work。

---

## 2026-05-18（晚）— 第一張 4×5 factorial sweep 出爐

`scripts/demo_grid_view.py` 從 1×5（BLF only）擴成 **4×5（BLF / NFS / FFS / BFS × 5 preset）**，僅改 2 行 import + heuristics list；圖存於 `code/figures/grid_view_seed42.png`。第 3 週的主交付物原型已產出，比預期早一週。

### 量化表（n=200, seed=42, bin=50×50）

```
              light_dep  heavy_dep  mixed   small   large
BLF  peak PE    74%        74%       68%    21%    79%
     discard    10%         9%        2%     0%    46%
NFS  peak PE    24%        24%       27%    19%    29%
     discard    88%        88%       88%    57%    96%
FFS  peak PE    35%        35%       31%    19%    34%
     discard    84%        84%       84%    31%    96%
BFS  peak PE    35%        35%       31%    19%    34%
     discard    85%        85%       85%    31%    96%
```

### 視覺對比（一眼可見的 mode 形狀）

- **BLF**：brick-wall（磚塊咬合）
- **NFS / FFS / BFS**：horizontal stripe（水平條紋）——shelf 家族通用 mode 形狀，與 BLF 截然不同
- BLF 在 packing density 全面領先 shelf 家族 30+ pp peak PE，但 shelf 家族在 small_items 上 PE 落差縮到 ~2 pp（19% vs 21%）——shelf 家族對 small_items 沒那麼吃虧

### Mode 命名候選（從 4×5 圖直接讀出來）

| 候選 mode | 出現位置 | 視覺特徵 |
|---|---|---|
| Brick-wall packing | BLF 行通用 | 磚塊互咬，少縫 |
| Horizontal stripe / shelf-locked | NFS/FFS/BFS 行通用 | 整齊水平條 + 大量空條 |
| Inland Island | BLF × heavy_departure | 中央留 item 被早到者包圍 |
| Top sliver | BLF × large_items | 上方水平條狀空白 |
| Shelf abandonment | NFS 全行 | 已關閉 shelf 上的廢棄空隙 |
| Item-too-tall failure | NFS/FFS/BFS × large_items | shelf 撐不下，幾乎全 discard |

### 待追證據（不要鎖死當結論）

> SUPERSEDED 2026-05-19：以下三項已於第 3 週收尾全部處理 → see experiments.md#2026-05-19

- **FFS ≈ BFS 重合**：peak PE 完全相同、discard 只差 1 pp、視覺幾乎一致。當前 seed=42、n=200、bin=50×50 下 best-fit 與 first-fit 退化到同支
  - 可能原因：bin/item 比小 → 候選 shelf 少 → 兩個 selection rule 常選到同一個。需 seed sweep（≥ 10 seeds）+ bin 大小掃描驗證是真的重合還是 seed-specific artefact
- **mean/peak PE ratio** 第三個 mode signature 候選元件還沒套到 4×5（只在 BLF × 5 算過）
- **fragmentation metric**（周長² shape factor）已實作但**還沒套到 sweep**——下一步可加進 annotation 變第三個數字，量化 sliver 強度

### 第 3 週剩餘工作（相對原計畫）

- ✅ 4×5 factorial 原型（提前完成）
- ⏳ seed sweep（≥ 10 seeds）確認 FFS ≈ BFS 是否穩定
- ⏳ fragmentation metric 套到 sweep
- ⏳ 蒐集 bin 狀態時序快照（非 peak only），準備第 4 週命名 mode

---

## 2026-05-18 RL 評估架構與 NP-hard 參數設定

> 三段方法論決策（RL 兩層評估架構 / RL 多軸選擇 / NP-hard 三層參數架構）已搬到 → research-decisions 2026-05-18，本檔不再保留以避免雙寫。進階 6 設計 RL 實驗前直接讀 research-decisions 即可。

---

## 2026-05-12

- 尚未開始實作；待選題定下後啟動 baseline 實驗
