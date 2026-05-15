# 靈感與發想

> 紀錄研究點子、候選題目、跨領域聯想、未來可能延伸的方向。
> 格式：`## YYYY-MM-DD` 為段落標題，最新日期置頂。

---

## 2026-05-14

### 變體 E（failure mode taxonomy 失敗模式分類學）的未來延伸方向

Special Topic 階段只實作 taxonomy 本身；報告結尾明示「未來可往 6 / 8 兩條 map（對應）」，作為碩論候選方向。

**進階 6：Mode 當 RL state feature（模式作為強化學習狀態特徵）**
- 把命名的 failure mode label 加進 RL agent（強化學習代理）的 state representation（狀態表示）
- 給 agent 注入 inductive bias（歸納偏置）：看到「目前 mode = Sliver」→ 學對應策略
- 預期 sample efficiency（樣本效率）勝過無 mode 標籤的純 baseline
- 風險：依賴 RL 訓練本身能跑；對楊老師方向不直接對齊（偏 ML 系統）

**進階 8：Cross-domain transfer（跨領域遷移）**
- 把 abstract taxonomy 套到具體場域，驗證 mode 是否普適：
  - FPGA partial reconfiguration（部分重組）
  - Cloud VM placement（雲端虛擬機調度）
  - KV-cache fragmentation（鍵值快取碎片，LLM 推論）
- 若跨域出現相同 mode 集合 → taxonomy 升格為 universal framework（普適框架）
- **與 5/12「碩論場域延後」決策的耦合點**：cross-domain 驗證流程恰好是「實驗驗證後再選場域」的天然路徑——做 cross-domain scan，看哪個場域最容易產生 distinct mode、最對接產學連結，再鎖場域

**為什麼挑 6 + 8 而非 1/2/3/4/5/7**：
- 6 = ML 系統路線天花板（潮、影響力高）
- 8 = 場域路線天花板（與碩論場域選擇直接耦合，且保留選擇權）
- 1/2/3 偏戰術改良，可被 6 或 8 吸收（mode-aware policy 可由 RL agent 學出）
- 4 偏視覺化補強，當 E 主體已涵蓋
- 5/7 偏 OR 理論，不符合 GIMT 系所定位

---

## 2026-05-12

### Dynamic 2D BP 仍有空間的方向（變體候選軸）

- **Dynamic with departures + repacking cost**：item 會離開、重排有成本、是否該重排是 meta-decision。比 online（只進不出）少很多 paper
- **Learning-based（2D online with departures）**：Deep RL / imitation learning，比 3D static（Zhao 2021、AlphaPack 等已熱）冷門
- **Multi-objective**：BP 文獻多只看 utilization，實務還要看取件時間、平衡、阻塞風險、退化／時效
- **Domain-specific constraint richness**：堆疊高度限制、易碎品分隔、溫區、出貨順序、due date、AGV 走道留白——每多一個都讓 textbook heuristic 失效

### 可能的應用場域（待文獻探索 + 老師討論）

- 雲端 VM placement（資料公開、模擬器成熟）
- 半導體 cassette buffer / FOUP 儲位
- 倉儲動態儲位（含 ABC 分級、揀貨頻次）
- 貨櫃堆場 / yard planning
- 零售貨架補貨
- 製造業 WIP buffer（已寫入 `context/research-interests.md` 第 3 節的場域遷移構想）

### load-bearing 視覺化的四種角色

詳見 `research-decisions.md` 2026-05-12 段。重點：若希望視覺化在碩論裡是必要而非裝飾，需走 CNN feature extractor、HITL 介面、image-embedding failure clustering、或 algorithm steering 其中一條。

### 既有條目

- 初始建立檔案，Bin-Packing 候選題目詳細分析請見 `candidate-topics.md`
