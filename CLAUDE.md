# CLAUDE.md — 研究資料夾說明

For tokens efficiency, if you have to think heavily / process disposable content(debugging, code review, scratch analysis), use English instead of Chinese.

---

## Memory Protocol（指令；對話啟動與寫入規則）

```yaml
on_conversation_start:
  read_first: memory.md             # 索引 + 題目定義 + 下次繼續 + 重要提醒（≤50 行）
  read_on_demand:                   # 按需展開，不要預先全讀
    decision_or_rationale: memory/research-decisions.md
    measurement_or_result: memory/experiments.md
    milestone_or_blocker:  memory/progress.md
    future_extension:      memory/ideas.md
    literature:            memory/literature-map.md
    archived_topic_eval:   memory/candidate-topics.md
    unsorted_stash:        memory/inbox.md

on_write:
  rule: single_source_of_truth          # 永不雙寫；資料只在 detail 檔出現一次
  classify_then_append:
    decision_or_rationale: memory/research-decisions.md   # 為什麼選 X、放棄什麼
    measurement_or_result: memory/experiments.md          # 跑了 X 得到 Y、踩雷
    milestone_or_blocker:  memory/progress.md             # 完成什麼、卡在哪
    future_extension:      memory/ideas.md                # 尚未做的延伸
    unclear:               memory/inbox.md                # consolidation 時 drain
  section_header: "## YYYY-MM-DD（可選 topic-tag）"        # 最新置頂
  cross_link: "→ exp YYYY-MM-DD" / "→ decisions YYYY-MM-DD"  # 禁止複製表格、數字
  update_memory_md_only_when: 「題目定義」「下次繼續」「重要提醒」實質變動
  date_format: ISO YYYY-MM-DD；相對日期一律轉絕對

on_supersede:
  trigger: 新事實使舊條目過期（含「假設→已驗證」轉變）
  action: 舊條目上方插入 marker，**不刪**；保留思考軌跡
  marker_format: |
    > SUPERSEDED YYYY-MM-DD：<原因一句話> → see <檔案>#<新日期>

hypothesis_vs_result:
  rule: 候選命名、預期 mode、未驗證 mapping 一律標 [假設]；驗證後改 [已驗證 YYYY-MM-DD]
  reason: E 變體的貢獻正是把假設變證據；混淆會誤判 prior art 與自己貢獻

consolidation:
  trigger: 使用者輸入「做一次 memory consolidation」／週末／sprint 邊界
  steps:
    - dedup:         跨檔重複片段，保留 detail 檔版本，其他改 link
    - mark_supersede: 過期條目加 marker（不刪）
    - drain_inbox:   inbox.md 條目分類進對應檔
    - refresh_index: 更新 memory.md 的「下次繼續」「題目定義」「重要提醒」
    - archive:       條目 ≥30 天未動 AND 已 superseded → memory/archive/YYYY-Qn.md

language:
  research_content: 中文（與 user 對齊）
  scratch_thinking: 英文（debugging / code review / 一次性分析，省 token）

current_focus_pointer:                  # 取代舊「當前進度」段；source of truth 在 memory.md
  see: memory.md → 「題目定義」「下次繼續」
```

---

## 專案定位

這個目錄是碩士論文的全程工作資料夾，涵蓋從研究發想、題目收斂、文獻延伸、開發實作，到最終論文撰寫的所有階段。

- 學校：國立臺灣科技大學（NTUST）
- 系所：智慧製造科技研究所（GIMT）
- 指導教授：楊傳凱（Chuan-Kai Yang），資訊管理系

---

## 目錄結構與各檔案角色

research/
├── CLAUDE.md          # 本文件，提供 Claude 專案背景與當前進度
├── memory.md          # 跨對話記憶索引：題目定義、下次繼續、重要提醒（對話啟動必讀，≤50 行）
├── journal.md         # 研究日誌：焦點演變、想法迭代、放棄的方向
├── meeting-notes.md   # 與指導教授的會議紀錄
├── memory/                          # 研究筆記層（detail 檔；按需展開）
│   ├── research-decisions.md        # 研究方向／實驗設定／方法論決策（**為什麼選 X**）
│   ├── experiments.md               # 跑了 X 得到 Y（資料、表格、踩雷）
│   ├── progress.md                  # 里程碑、卡關、週時程實況
│   ├── ideas.md                     # 未來延伸方向、跨領域聯想
│   ├── candidate-topics.md          # 候選題目完整分析（archive 性質）
│   ├── literature-map.md            # 文獻掃描中心：方法家族、survey、H1–H5 操作指引
│   ├── inbox.md                     # 未分類暫存，consolidation 時 drain
│   └── archive/                     # 季 archive（≥30 天未動 AND 已 superseded 的條目）
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
