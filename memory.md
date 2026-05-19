# Memory — 跨對話記憶索引

> 每次對話開始時讀取本檔案。需要更細節時，再讀 `memory/` 內對應分類檔案。

---

## 題目定義（2026-05-12 鎖定，2026-05-14 narrative 收斂至 E）

**Dynamic 2D Rectangle Bin Packing**：把為 static 設計的 2D placement 啟發式（BLF / NFS / FFS / BFS）放到有 arrival + departure 的 dynamic 環境下跑，觀察它們的**退化行為與失敗模式**。

- **Framing**：abstract（不綁特定場域；用 Hopper-Turton / Berkey-Wang benchmark + 合成 arrival/departure）
- **Narrative（2026-05-14 收斂）**：**E 變體 — failure mode taxonomy 失敗模式分類學**
  - 一個月內實作 E：跑多 heuristic × 多 workload，命名 + 量化 + 視覺化失敗模式，產出 taxonomy 對照表
  - 5/14 positioning scan 顯示 E 沒有直接 prior art（FPGA 圈僅做 fragmentation metric 不做分類學），差異化空間「強」；A 的軌道被 Burcea 2014 / Wong 2009 競爭分析 + RL baseline 圈搶走，差異化空間「中強」
- **未來延伸（報告結尾要明示）**：E 完成後可 map（對應）到兩條碩論方向
  - **進階 6（Mode 當 RL state feature 模式作為強化學習狀態特徵）**：把 mode label 加進 agent state representation，給 RL 注入 ind  uctive bias
  - **進階 8（Cross-domain transfer 跨領域遷移）**：把 taxonomy 套到 FPGA / Cloud VM / KV-cache 等場域驗證普適性，並作為碩論場域選擇的天然篩選流程
- **報告結尾 bar**（2026-05-12 釐清）：不解決問題，但要立得起 next optimization target——結尾必須能講出「現有方法已優化到 X、我觀察到的 gap 是 Y、下一步可從 6 或 8 切入」
- **Abstract framing 的立論基礎**：不靠 gap 大小，靠**保留選擇權**（場域選擇延至碩論階段，且由進階 8 的驗證流程支撐）

---

## 當前進度（2026-05-18 晚更新）

- **研究階段**：Special Topic narrative 鎖定（變體 E），**第 3 週原型提前完成**
- **Special Topic 題目**：Dynamic 2D Rectangle BP + abstract framing + **E 變體 failure mode taxonomy**
- **本月目標**：1 個月內實作 E + 視覺化原型 + 報告
- **關鍵日期**：6/8 報告週前 8 成完成

### 4 週時程實況

| 週次 | 內容 | 狀態 |
|---|---|---|
| **第 1 週** | BLF baseline + Simulator + viz + tests | ✅ **完成**（5/14 開工，5/15 git push） |
| **第 2 週** | Workload generator + metrics + animation | ✅ generator + 5 presets + 3 metrics + grid view；animation 暫略 |
| **第 3 週** | NFS/FFS/BFS + factorial 掃描 | 🟢 **原型已出**（4 heuristic 全實作，4×5 grid 跑通；剩 seed sweep / fragmentation 套用） |
| 第 4 週 | 命名 mode + signature + mitigation 對照表 + 寫報告 | ⏳ 未開始（候選 mode 已從 4×5 圖讀出 6 個，見下） |

### 第一個 4×5 factorial 證據（n=200, seed=42, bin=50×50）

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

詳見 `code/figures/grid_view_seed42.png` 與 `memory/experiments.md` 2026-05-18（晚）段。

### Mode 命名候選（6 個，從 4×5 圖直接讀出）

1. **Brick-wall packing**（BLF 行通用）
2. **Horizontal stripe / shelf-locked**（NFS/FFS/BFS 行通用）
3. **Inland Island**（BLF × heavy_departure）
4. **Top sliver**（BLF × large_items）
5. **Shelf abandonment**（NFS 全行）
6. **Item-too-tall failure**（NFS/FFS/BFS × large_items）

第 4 週 fallback 檢核點「≥ 3 個 distinct mode」已遠超門檻，**不需退回變體 A**。

### 待追證據（不要當結論）

- **FFS ≈ BFS 重合**：當前 seed/n/bin 下兩者數值與視覺幾乎一致；需 seed sweep（≥10 seeds）+ bin 大小掃描，確認是真重合還是 artefact
- **mean/peak PE ratio** 第三個 signature 元件還沒套到 4×5
- **fragmentation metric** 已實作但還沒套到 sweep annotation

## 下次繼續（從另一設備接續時讀這段）

- **實驗設計查表**：2026-05-18 已把 RL 評估兩層架構（訓練 vs 評估、optimal 分層）、多軸選擇（sample efficiency / generalization / robustness / hard-case，不單押 final PE）、NP-hard 參數設定三層架構（benchmark family / factorial sweep / regime stratification）整理進 `memory/experiments.md`。進階 6 設計 RL 實驗前直接查表

### 立即下一步（第 3 週收尾 / 第 4 週啟動）

1. **seed sweep** 驗證 FFS ≈ BFS 是否穩定（≥10 seeds，相同 n / bin），同時看其他 cell 的 seed-to-seed variance；若 FFS=BFS 跨 seed 穩定，當作觀察寫進報告；若 seed-specific，找分歧 seed 寫進報告當「兩者並非總是等價」的反例
2. **fragmentation metric 套到 4×5 annotation**——把 grid view annotation 從 2 個數字（peak PE / discard）擴成 3 個（+ peak-time F），量化 sliver 強度；BLF × large_items 應該明顯高
3. **mean/peak PE ratio 補做完整 4×5**——目前只有 BLF 那列算過，看 shelf 家族 ratio 是否也呈規律
4. **時序快照採集**（非 peak only）：第 4 週命名 mode 前需要看到 mode 如何成形/消解，不能只看 peak frame；snapshot 已存 `result.snapshots`，需設計 sampling 策略

### 第 4 週要做

命名 mode → 寫 signature（用 PE ratio + fragmentation + 視覺特徵組合）→ 寫 mitigation 對照表 → 寫報告（含結尾的進階 6 / 8 future work 段）。**fallback 已 clear**：6 個 mode 候選 >> 3 個門檻。

### 平行 / 可選

- **prior work 細讀**：Burcea 2014 / Wei 2011 IJCAI / Powers 2023 全文——確認他們確實沒做 taxonomy（mode 命名前要做）
- 約楊老師 sanity check Special Topic 方向
- 將近期轉折寫進 `journal.md`（位於 `for my self, don't revise/`）

### 程式相關指令（在 `code/` 內執行）

```bash
cd code && uv sync                                    # 首次或換設備：安裝依賴
cd code && uv run pytest                              # 75 tests 全綠
cd code && uv run python scripts/demo_workload.py heavy_departure  # 單 workload demo
cd code && uv run python scripts/demo_grid_view.py    # 4×5 factorial sweep → figures/grid_view_seed42.png
```

## 重要提醒

- 重思考／一次性內容（debugging、code review、scratch analysis）用英文以節省 token，最終產出用中文
- 本專案 memory 系統與 harness 自動 memory（`~/.claude/projects/.../memory/`）並存、互不干擾
- 寫入記憶時：在對應分類檔案最上方新增 `## YYYY-MM-DD` 段落，最新日期置頂
- 對未拍板的方向，記錄時要區分「已釐清的理解」vs「尚待決定的選項」，不要寫成已決定
- **場域選擇延後**：Special Topic 階段刻意不綁特定 home application；FPGA 只當文獻背景知識，不當研究場域
- **碩論貢獻評估**先不套用於 Special Topic 選題——會癱瘓選題決策

---

## 索引

- [research-decisions.md](memory/research-decisions.md) — 研究方向決策、放棄的方向、選題理由
- [progress.md](memory/progress.md) — 階段性進展、里程碑、卡關狀況
- [ideas.md](memory/ideas.md) — 研究點子、跨領域聯想、零散發想
- [candidate-topics.md](memory/candidate-topics.md) — Bin-Packing 候選題目完整分析（篩選判準、軸組合、視覺揭露力）
- [literature-map.md](memory/literature-map.md) — 文獻掃描中心檔案：方法家族、關鍵字、必讀 survey、第一輪查詢、操作指引（H1–H5 假設驅動）
- [experiments.md](memory/experiments.md) — 實作過程、踩過的雷、baseline 結果、資料來源
