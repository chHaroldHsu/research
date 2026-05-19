# CLAUDE.md — 研究資料夾說明

For tokens efficiency, if you have to think heavily / process disposable content(debugging, code review, scratch analysis), use English instead of Chinese.

---

## 對話啟動程序

**每次對話開始前，必須先讀取 `memory.md`**，掌握跨對話的進度、下次繼續的地方、重要提醒。需要更細節時，再依索引讀取 `memory/` 內對應分類檔案。

寫入記憶時：在 `memory/` 對應分類檔案最上方新增 `## YYYY-MM-DD` 段落，最新日期置頂；必要時同步更新 `memory.md` 的「當前進度」「下次繼續」「重要提醒」。

---

## 當前進度

> 此章節最常更新，反映研究的即時狀態。

**研究階段**：題目已鎖定，進入 positioning scan + baseline 實作

**當前聚焦方向**：Dynamic 2D Rectangle BP（abstract framing），先做 positioning scan 釐清現有方法邊界，再進入 baseline 實作

**To-dos**：
- [x] **本週選題**（5/10 前）：**已鎖定** Dynamic 2D Rectangle BP + abstract framing（不綁特定場域），narrative（A 原版 vs E 變體）5/31 前決定。詳見 `memory.md` 題目定義段
- [ ] **2–3 天 positioning scan**：先讀 `memory/literature-map.md` 列的 3 篇 survey（Christensen 2017 / Lodi 2002 / Coffman 2013），再依關鍵字延伸；回答「別人優化過什麼 / 邊界在哪 / 我的觀察落在哪個邊界外」
- [ ] **第 1–2 週**：2D BLF baseline + 合成 arrival/departure workload generator（Hopper-Turton benchmark 改造）
- [ ] **5/31 前**：根據實作結果決定 narrative（A 原版 = heuristic 退化比較 / E 變體 = failure mode taxonomy）
- [ ] **6 月前**產出視覺化原型（即使只是 baseline 跑得出來、能畫出結果的版本）
- [ ] **6/8 報告週前**完成 8 成報告內容（題目動機、baseline、初步結果、視覺化 demo），結尾立得起 next-step claim

---

## 專案定位

這個目錄是碩士論文的全程工作資料夾，涵蓋從研究發想、題目收斂、文獻延伸、開發實作，到最終論文撰寫的所有階段。

- 學校：國立臺灣科技大學（NTUST）
- 系所：智慧製造科技研究所（GIMT）
- 指導教授：楊傳凱（Chuan-Kai Yang），資訊管理系

---

## 目錄結構與各檔案角色

```
research/
├── CLAUDE.md          # 本文件，提供 Claude 專案背景與當前進度
├── memory.md          # 跨對話記憶索引：當前進度、下次繼續、重要提醒（對話開始必讀）
├── journal.md         # 研究日誌：焦點演變、想法迭代、放棄的方向
├── meeting-notes.md   # 與指導教授的會議紀錄
├── memory/                          # 研究筆記層
│   ├── research-decisions.md        # 研究方向決策、放棄的方向、選題理由
│   ├── progress.md                  # 階段性進展、里程碑、卡關狀況
│   ├── ideas.md                     # 研究點子、跨領域聯想、零散發想
│   ├── candidate-topics.md          # Bin-Packing 候選題目完整分析
│   ├── literature-map.md            # 文獻掃描中心：方法家族、關鍵字、survey 入口、H1–H5 假設驅動操作指引
│   └── experiments.md               # 實作過程、踩過的雷、baseline 結果、資料來源
├── context/                         # 研究背景層
│   ├── advisor.md                   # 指導教授研究背景、學生論文方向、方法論特徵
│   ├── department.md                # 系所定位、三大專業領域、論文題目隱含要求
│   ├── topic-fit-framework.md       # 論文選題的三維度契合度判斷框架
│   └── research-interests.md        # 個人研究興趣領域、視覺化定位、場域遷移構想
├── paper/                           # 文獻 PDF（已下載的關鍵論文）
└── code/                            # 程式碼層（所有實作放這裡，獨立 uv 專案）
    ├── pyproject.toml               # uv 專案設定 + 依賴清單
    ├── uv.lock
    ├── .gitignore                   # code 專屬 ignore（venv / __pycache__ / 產出物）
    ├── dyn2dbp/                     # 主套件
    │   ├── core/                    # Item / BinState / Simulator
    │   ├── heuristics/              # PlacementStrategy ABC + BLF / NFS / FFS / BFS
    │   ├── workloads/               # 合成 arrival/departure workload generator
    │   ├── metrics/                 # PE、fragmentation metric、mode signature
    │   ├── viz/                     # snapshot、animation、H×W 網格視覺化
    │   └── experiments/             # factorial sweep runner
    ├── tests/                       # pytest（測試 BinState / BLF / Simulator 不變量）
    ├── scripts/                     # 一次性的 demo / 探索腳本
    ├── notebooks/                   # Jupyter 探索用
    ├── data/snapshots/              # 採集到的 bin 狀態時序快照（不入 git）
    └── figures/                     # 產出的圖（不入 git）
```

**程式相關所有指令在 `code/` 內執行**：
- 跑測試：`cd code && uv run pytest`
- 跑 demo：`cd code && uv run python scripts/demo_blf.py`
- 起 Jupyter：`cd code && uv run jupyter lab`

---

## 研究背景

### 一、指導教授：楊傳凱（Chuan-Kai Yang）

> 若需要了解指導教授的研究背景，請閱讀 `context/advisor.md`。

### 二、系所：智慧製造科技研究所（GIMT, NTUST）

> 若需要了解系所背景、關注領域及論文題目隱含要求，請閱讀 `context/department.md`。

### 三、論文選題的契合度判斷框架

> 若需要使用三維度（方法論 / 系所 / 可行性）檢視候選題目，請閱讀 `context/topic-fit-framework.md`。

### 四、個人研究興趣與題目發想

> 若需要了解個人興趣領域、視覺化定位與場域遷移構想，請閱讀 `context/research-interests.md`。
