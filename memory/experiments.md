# 實驗紀錄

> 紀錄實作過程、踩過的雷、技術細節、baseline 結果、資料來源。
> 格式：`## YYYY-MM-DD` 為段落標題，最新日期置頂。

---

## 2026-05-18

### 方法論決策：RL 評估的兩層架構

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

### 方法論決策：NP-hard 問題的參數設定處理（三層架構）

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

---

## 2026-05-12

- 尚未開始實作；待選題定下後啟動 baseline 實驗
