# TW ETF Dashboard — 台灣ETF智能分析儀表板
> ## 🛍️ **ETF 儀表板 — 完整版**
> 此 repo 為開源核心。完整版 **[ETF 儀表板 ($29) on Gumroad](https://slashmaster6.gumroad.com/l/etf-dashboard)** — 自動財報分析、評分系統、歷史回測與每日更新。


> 自動爬取 TWSE/TPEX/Yahoo Finance 資料，對 0050、0056、00878、00713、006208 成分股進行多維度財務與技術分析，並發布為 GitHub Pages 靜態網站。

**線上網址：** https://slashmantools.us/tw-etf-dashboard/dashboard.html

---

## 目錄

1. [架設步驟](#架設步驟)
2. [資料夾與檔案結構](#資料夾與檔案結構)
3. [網站地圖](#網站地圖)
4. [資料來源與頁面說明](#資料來源與頁面說明)
5. [技術指標計算方式](#技術指標計算方式)
6. [選股邏輯與評級系統](#選股邏輯與評級系統)
7. [評級升降機制](#評級升降機制)
8. [部署流程](#部署流程)

---

## 架設步驟

### 環境需求

- Python 3.9+
- 套件：`yfinance numpy pandas`
- GitHub 帳號 + Personal Access Token（PAT，需 `repo` 寫入權限）

```bash
pip install yfinance numpy pandas
```

### 首次設定

1. **Fork 本 repo 並啟用 GitHub Pages**
   Settings → Pages → Branch: `main` / 根目錄 → 儲存

2. **設定 PAT**
   在 `_github_push.py`、`_push_reports.py`、`_push_src.py` 中替換：
   ```python
   PAT = "ghp_your_personal_access_token"
   ```
   > ⚠️ 請勿將含有真實 PAT 的檔案 commit。`_push_src.py` 上傳時會自動遮蔽。

3. **取得成分股清單並執行首次分析**（見[部署流程](#部署流程)）

---

## 資料夾與檔案結構

```
GitHub repo (slashman413/tw-etf-dashboard)
├── dashboard.html          ← 自動產生的 SPA，GitHub Pages 服務此檔
├── series_map.json         ← 465 支股票 K 線 + 指標時間序列（~3.3MB）
├── reports/                ← 每日分析報告，以日期為子資料夾
│   └── YYYY-MM-DD/
│       ├── composite_data.json       ← 主要ETF成分股財務彙整
│       ├── expansion_stocks.json     ← 0056/00878 等擴展成分股
│       ├── grand_unified.json        ← 綜合四維度排名
│       ├── dna_full_market.json      ← 全市場 DNA 6訊號掃描結果
│       ├── full_market.json          ← 全市場 1969+ 家財務快照
│       ├── quarterly_financials.json ← MOPS Q1 季報（損益+資產負債）
│       ├── bwibbu_fresh.json         ← TWSE 最新本益比/殖利率
│       ├── price_momentum.json       ← 價格動能
│       ├── ma_refresh.json           ← 30日均線
│       ├── conviction_data.json      ← 信念分分析
│       ├── conviction_matrix.json    ← 確信矩陣
│       ├── institutional_flows.json  ← 法人買賣超（T86）
│       └── stocks/                   ← 個股詳細報告（Markdown）
└── src/                    ← Python 原始碼備份（129 支腳本）

本地工作目錄 (multi-agent/)
├── build_dashboard.py      ← 核心：將所有 JSON 組裝成 dashboard.html
├── series_map.json         ← 本地 K 線快取
├── _github_push.py         ← 推送 dashboard.html + series_map.json
├── _push_reports.py        ← 批次推送 reports/ 資料夾
├── _push_src.py            ← 推送原始碼至 GitHub src/（自動遮蔽 PAT）
│
├── 資料爬取腳本
│   ├── full_market_crawl.py     ← BWIBBU_ALL + STOCK_DAY_ALL + TPEX
│   ├── mops_quarterly_crawl.py  ← MOPS 季報爬取
│   ├── daily_refresh.py         ← 每日收盤價格快速更新
│   ├── bwibbu_refresh.py        ← 本益比/殖利率更新
│   ├── crawl_ohlcv.py           ← Yahoo Finance K 線
│   └── institutional_flows.py   ← 法人買賣超 T86
│
├── 分析計算腳本
│   ├── composite_score.py       ← 財務複合分（0–100）
│   ├── grand_unified.py         ← 四維度綜合評分
│   ├── dna_full_market.py       ← 全市場 DNA 6訊號技術篩選
│   ├── conviction_list.py       ← 信念分排名
│   ├── conviction_matrix.py     ← 確信矩陣
│   ├── price_momentum.py        ← 動能計算
│   ├── ma_refresh.py            ← 均線計算
│   └── sector_analysis.py       ← 產業分析
│
└── 工具腳本
    ├── _patch_series_map.py     ← 補充缺少 K 線的股票
    ├── _probe_date.py           ← 探測 TWSE 最新資料日期
    └── _verify_sm.py            ← 驗證 series_map 完整性
```

---

## 網站地圖

網站為 SPA（Single Page Application），所有頁面透過左側導覽列切換，無需重新載入。

### 🏠 主要頁面

| 頁面 | 說明 |
|------|------|
| **總覽** | 高信心標的表、漲跌排行、營收動能前8名。點擊任一股票彈出 K 線 + 布林通道彈窗 |
| **全市場** | 1969+ 家上市櫃公司財務快照，可按 P/E、殖利率、EPS 排序 |

### ⭐ 精選推薦

| 頁面 | 說明 |
|------|------|
| **綜合行動信號** | DNA + 財務 + 動能三合一即時操作建議（買進/觀望/賣出）|
| **推薦排名** | 三子頁：最強推薦（信念分≥65）/ 確信矩陣 / 綜合排名（Grand Unified）|
| **TRIPLE 精析** | 🚀 Triple Confirmed 股票深度報告 |
| **週一行動** | 每週開盤前重點操作計劃 |
| **開盤行動卡** | 當日快速操作清單（進場/觀察/迴避）|
| **監控警示** | 即將觸發 DNA 訊號的股票警示清單 |
| **法人買賣超** | 外資/投信每日買賣超（T86 端點，張數）|
| **智慧資金匯合** | 法人動向 + 技術 + 基本面三合一確認 |

### 🔎 選股分析

| 頁面 | 說明 |
|------|------|
| **選股器** | 多條件篩選：評級 / 產業 / 融資信號 / 綜合分，可點選表頭排序 |
| **4月營收** | 2026/04 月營收 YoY、累計YoY、前兩名產業 |
| **5月預告** | 5月營收預估與趨勢 |
| **盈利品質** | EPS 可重複性、一次性項目佔比、現金流品質 |
| **股息日曆** | 除息日期、配息金額、殖利率 |
| **股息安全** | 配息可持續性（EPS覆蓋率、負債比）|
| **股息收入預測** | 輸入持股數量，估算年度配息收入 |
| **Q2 預估 EPS** | 2026 Q2 EPS 前瞻（依 Q1 基礎推算）|

### 🧬 技術分析

| 頁面 | 說明 |
|------|------|
| **大飆股 DNA** | 全市場 437+ 支 DNA 技術篩選；頂部產業熱圖（點擊篩選產業），表格列可點擊開 K 線+DNA 指標彈窗 |
| **升評觸發計算** | 各指標距觸發線差距，計算需達到什麼股價/數值才能觸發各訊號 |
| **回測驗證** | DNA 策略勝率歷史統計 |
| **相對強度** | 個股 vs 大盤 相對強度排行 |
| **價格動能** | 30日均線偏離度 + 動能排行 |
| **技術分析** | RSI / 布林通道 / MACD 摘要 |

### 📊 估值分析

| 頁面 | 說明 |
|------|------|
| **估值更新** | 最新 BWIBBU P/E、P/B、殖利率（TWSE 即時資料）|
| **目標價** | DCF / 本益比法 目標價計算與上漲空間 |
| **同業比較** | 同產業內估值橫向比較 |
| **升評路徑** | 各指標需改善多少才能晉升下一個評級 |
| **風險/PEG** | PEG 比率（本益比÷EPS成長率）與下行風險評估 |
| **安全邊際** | Graham 安全邊際計算（內在價值 vs 市價折扣）|

### 💼 投資組合

| 頁面 | 說明 |
|------|------|
| **倉位計算** | Kelly 公式 / 固定比例 倉位建議 |
| **組合優化** | 最大化 Sharpe 比率 / 最小化波動度 |
| **投資組合** | 持倉追蹤、損益計算 |
| **融資融券** | 融資可用額度、融券成本、融資維持率 |
| **交易設置** | 進場點、停損點、目標價三點位設定 |
| **情境分析** | 牛市/熊市/基本情境 EPS 模擬 |

### 🏭 產業 ETF

| 頁面 | 說明 |
|------|------|
| **產業資訊** | 四子頁：產業分析 / 產業熱圖（點擊篩選）/ 板塊輪動 / 產業總覽 |
| **ETF 集中度** | 0050/0056/00878 前10大成分股比重 |
| **ETF 比較** | 各ETF績效、殖利率、波動度橫向比較 |
| **上櫃分析** | TPEX 上櫃股票 Q1 財務分析（OTC 端點）|
| **成分調整** | ETF 定期調整預測與影響 |
| **AI 供應鏈** | AI/半導體供應鏈個股分析 |

---

## 資料來源與頁面說明

### TWSE 開放 API

> ⚠️ 頻繁查詢會導致 IP 封鎖。**每個端點之間至少等待 132 秒**。

| API 端點 | 資料內容 | 使用頁面 |
|---------|---------|---------|
| `exchangeReport/STOCK_DAY_ALL` | 全市場收盤價、成交量 | 總覽、動能、均線 |
| `exchangeReport/BWIBBU_ALL` | 全市場本益比、殖利率、股價淨值比 | 估值更新、選股器 |
| `exchangeReport/t86` | 外資/投信每日買賣超（張數）| 法人買賣超 |
| `opendata/t187ap14_L` | MOPS 季報損益（上市）| Q1 財務、選股器 |
| `opendata/t187ap06_L` | MOPS 季報資產負債（上市）| 安全邊際、盈利品質 |
| `opendata/t187ap05_L` | MOPS 月營收（上市）| 4月/5月營收 |
| `opendata/t187ap14_O` | MOPS 季報損益（上櫃）| 上櫃分析 |
| `opendata/t187ap05_O` | MOPS 月營收（上櫃）| 上櫃分析 |

Base URL: `https://openapi.twse.com.tw/v1/`

### Yahoo Finance（yfinance）

| 資料 | 週期 | 說明 |
|-----|------|------|
| 日線 OHLCV | 2年 | K 線圖、DNA 技術指標計算 |
| 格式 | `[日期, 開盤, 收盤, 最低, 最高]` | ⚠️ 第2欄為**收盤**，非最高價 |

無速率限制，可批次下載。

---

## 技術指標計算方式

### 大飆股 DNA — 6 個技術訊號

| # | 訊號 | 時間框架 | 計算 | 觸發條件 |
|---|------|---------|------|---------|
| S1 | +DI(1) | 月線 | DMI 正向指標，Wilder 平滑 n=1 | **> 50** |
| S2 | RSI(4) | 月線 | RSI，週期 4（≈84 交易日）| **> 77** |
| S3 | W%R(50) | 日線 | Williams %R，週期 50 | **< 20**（強勢區）|
| S4 | RSI(60) | 日線 | RSI，週期 60 | **> 57** |
| S5 | VR(2) | 週線 | 成交量比率，週期 2（≈10 交易日）| **≥ 150** |
| S6 | VR(2) | 月線 | 成交量比率，週期 2（≈42 交易日）| **≥ 150** |

**Williams %R：**
```
W%R(n) = (HH_n − Close) / (HH_n − LL_n) × 100
HH_n = n期最高，LL_n = n期最低
0 = 極強（貼近高點），100 = 極弱（貼近低點）
S3 條件：W%R < 20 代表股價強勢突破高點區域
```

**Volume Ratio (VR)：**
```
A = n期上漲日成交量總和
B = n期下跌日成交量總和
C = n期平盤日成交量總和
VR = (A + C/2) / (B + C/2) × 100
> 150 = 多頭積極，買盤強於賣盤
```

**RSI（Wilder EMA）：**
```
RS = EWM(上漲, α=1/n) / EWM(下跌, α=1/n)
RSI = 100 − 100 / (1 + RS)
```

**+DI（月線 DMI）：**
```
True Range = max(High−Low, |High−PrevClose|, |Low−PrevClose|)
+DM = max(High−PrevHigh, 0) 若 High−PrevHigh > PrevLow−Low
+DI(n) = EWM(+DM, n) / EWM(TR, n) × 100
```

### 布林通道 BB(20, 2)（總覽彈窗）

```
中軌(MB) = 20日收盤SMA
標準差(σ) = sqrt(Σ(Close − MB)² / 20)
上軌(UB) = MB + 2σ
下軌(LB) = MB − 2σ
```

K 線顏色（台股慣例）：漲紅（Close > Open）、跌綠（Close < Open）

---

## 選股邏輯與評級系統

### 四維度綜合評分（Grand Unified Score，滿分 100）

```
綜合分 = 基本面分(0–25) + DNA技術分(0–25) + 估值分(0–25) + 動能分(0–25)
```

#### 1. 基本面分
- 來源：`composite_score.py` 計算財務複合分（0–100）
- 考量：EPS 成長、營收 YoY、毛利率趨勢、Q1 EPS
- `fund_pts = composite_score / 100 × 25`

#### 2. DNA 技術分
```
tech_pts = (bull_signs / 6 × 15) + (core_met / 3 × 10)
bull_signs = S1–S6 中已觸發的訊號數（0–6）
core_met   = S3、S4、S5 核心訊號中已觸發數（0–3）
```

#### 3. 估值分（依本益比）

| P/E | 分數 | 備註 |
|-----|------|------|
| < 10 | 25 | 極度低估 |
| 10–15 | 22 | 便宜 |
| 15–20 | 18 | 合理 |
| 20–30 | 12 | 偏高 |
| 30–50 | 6 | 高估 |
| > 50 | 2 | 極度高估 |
| 不明 | 10 | 中性 |

殖利率加分：≥4.5% +3分，≥6.0% 再+2分（最多+5，上限25）

#### 4. 動能分
```
mom_pts = 12.5（基礎分）
         + min( 8, max(-8, 均線偏離% × 0.5))   # 30日均線位置 ±8
         + min( 5, max(-5, 動能% × 0.3))        # 近期漲跌 ±5
         + min( 5, 上漲空間 / 30)               # 目標價上漲空間 +5
```

---

## 評級升降機制

### 評級等級

| 評級 | 觸發條件 | 意義 |
|-----|---------|------|
| 🚀 **TRIPLE CONFIRMED** | 綜合分 ≥ 70 **且** DNA訊號 ≥ 3 | 財務/技術/估值/動能全面確認，最高信心度 |
| ✅ **STRONG BUY** | 綜合分 ≥ 65 | 高度複合確信，積極買入 |
| 📈 **BUY** | 綜合分 ≥ 55 | 正面訊號為主，可分批建倉 |
| 👀 **WATCH** | 綜合分 ≥ 40 | 觀察名單，等待確認訊號 |
| ⬛ **HOLD** | 綜合分 ≥ 25 | 持有，無明確方向 |
| ❌ **REDUCE** | 綜合分 < 25 | 減碼或迴避 |

### 升評路徑（升評觸發計算頁）

每支股票顯示距下一評級所需改善的項目：
- 財務複合分還差幾分
- 需要額外幾個 DNA 訊號
- P/E 需降至何水準
- 股價需達到均線的什麼位置

### DNA 訊號觸發參考值

| 訊號 | 觸發所需 |
|------|---------|
| S3 (日W%R<20) | 股價需站上50日高低區間的前20% |
| S4 (日RSI>57) | 60日RSI 需升至 57 以上 |
| S5 (週VR≥150) | 近10交易日買盤量 ≥ 賣盤量 1.5倍 |
| S6 (月VR≥150) | 近42交易日買盤量 ≥ 賣盤量 1.5倍 |
| S1 (月+DI>50) | 月線趨勢需持續向上，+DI超越50 |
| S2 (月RSI>77) | 月線長期強勢，RSI(84日)超越77 |

---

## 部署流程

### 每日完整更新（市場收盤後 14:30 起）

```bash
# 1. 全市場資料（包含 132s 等待）
python full_market_crawl.py

# 2. 法人買賣超
python institutional_flows.py

# 3. K 線資料（Yahoo Finance，無速率限制）
python crawl_ohlcv.py

# 4. 計算分析
python composite_score.py
python grand_unified.py
python dna_full_market.py

# 5. 建置並推送
python build_dashboard.py
python _github_push.py
```

### 快速價格更新（不需全量爬取）

```bash
python daily_refresh.py    # 僅更新價格+動能
python build_dashboard.py
python _github_push.py
```

### 備份

```bash
python _push_reports.py    # 備份 reports/ 至 GitHub
python _push_src.py        # 備份 Python 原始碼至 GitHub src/
```

---

## 已知限制

| 問題 | 說明 |
|------|------|
| 2823 中壽 | Yahoo Finance 無資料（已下市）|
| 2888 新光金 | 已與台新金(2887)合併，代碼作廢 |
| TWSE IP 封鎖 | 每個 API 端點間隔 < 2 分鐘即可能被封 |
| K 線資料 | 最近 120 個交易日，不含即時報價 |
| GitHub Pages | CDN 快取最長數分鐘，更新後需強制重新整理（Ctrl+Shift+R）|

### 🛒 相關產品
- [ETF 儀表板 — 完整版 ($29)](https://slashmaster6.gumroad.com/l/etf-dashboard?utm_source=github&utm_medium=referral) - 自動財報分析、評分系統、歷史回測與每日更新。
