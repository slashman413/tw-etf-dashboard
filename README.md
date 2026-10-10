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

- Python 3.11+
- 套件：`pip install -r requirements.txt`（CI 只需 `requirements-ci.txt`：共用 TWSE 函式庫 [`slashman-finance-utils`](https://github.com/slashman413/slashman-finance-utils)，純 stdlib）
- GitHub 帳號（`auto_push` 走本機 git 認證；僅 `push_key_files` 需要 PAT，`repo` 寫入權限）

```bash
pip install -r requirements.txt
python run.py --list        # 列出所有可執行模組（依層分組）
```

> 從舊版（腳本都在根目錄）升級的本機工作目錄：`git pull` 後執行一次
> `python run.py migrate_layout --apply`，把本機 `reports/` 與根目錄的 `taiex_*.json`
> 搬到新位置。

### 首次設定

1. **Fork 本 repo 並啟用 GitHub Pages**
   Settings → Pages → Branch: `main` / 根目錄 → 儲存

2. **設定 PAT（僅 `push_key_files` 需要）**
   PAT 一律從環境變數讀取（變數名稱由 `config.json` 的 `github_pat_env` 決定，預設 `GITHUB_PAT`），**絕對不要寫進任何 .py 檔**：
   ```bash
   export GITHUB_PAT=...          # 或寫進 .env（已 gitignore）後執行 set -a; . ./.env; set +a
   ```
   > ⚠️ 建議使用 fine-grained token，只授權本 repo 的 Contents: Read/Write。`auto_push` 與 GitHub Actions 不需要 PAT（分別使用本機 git 認證與內建 `GITHUB_TOKEN`）。

3. **取得成分股清單並執行首次分析**（見[部署流程](#部署流程)）

---

## 資料夾與檔案結構

```
tw-etf-dashboard/
├── dashboard.html          ← GitHub Pages 服務的 SPA（CI 每日更新，需追蹤）
├── series_map.json         ← K 線 + 指標時間序列；dashboard.html 執行時 fetch（CI 更新，需追蹤）
├── run.py                  ← 唯一入口：python run.py <模組名> [參數]
├── config.json             ← 本機設定（PAT 環境變數名稱、TWSE 等待秒數）
├── config/llm.toml         ← LLM 提示詞 + 模型設定（agents/ 唯一的 prompt 來源）
├── requirements.txt / requirements-ci.txt
├── assets/                 ← 內嵌進 dashboard 的圖片（QR code）
├── docs/                   ← 產生的長篇報告
├── data/
│   ├── seed/               ← 追蹤中的啟動快照（taiex_*.json、expansion_ohlcv.json、reports-2026-06-14/）
│   ├── raw/                ← 抓取的原始資料（gitignore）
│   └── reports/YYYY-MM-DD/ ← 分析輸出 JSON / Markdown（gitignore）
├── cache/                  ← 可丟棄的快取（gitignore）
├── src/twetf/
│   ├── paths.py            ← 所有路徑的唯一來源（以 repo 根目錄為錨點，與 cwd 無關）
│   ├── fetchers/           ← 抓資料：TWSE / TPEx / MOPS / Yahoo（full_market_crawl、bwibbu_refresh、crawl_ohlcv、institutional_flows…）
│   ├── analyzers/          ← 純計算：composite_score、grand_unified、dna_full_market、conviction_*、indicators…
│   ├── renderers/          ← 產出：build_dashboard、dashboard_consts、weekly_digest、export_csv…
│   ├── pipeline/           ← 編排：ci_update（GitHub Actions）、daily_refresh、dna_refresh、auto_push…
│   ├── oneoff/             ← 單次調查腳本（保留參考，不在任何流程中）
│   ├── agents/             ← LLM 代理（爬蟲摘要、資料萃取、code review、發想）
│   ├── llm/                ← LLM API 呼叫唯一入口（讀 config/llm.toml）
│   └── common/utils.py
└── tests/                  ← python -m unittest discover -s tests（PYTHONPATH=src）
```

資料規則：抓取結果寫 `data/raw/`，分析結果寫 `data/reports/<日期>/`，暫存寫 `cache/`——
三者皆不進 git。讀取時 `raw_or_seed()` 優先用 `data/raw/`，沒有才退回追蹤中的 `data/seed/`。
只有 Pages 需要的 `dashboard.html`、`series_map.json` 留在根目錄並由 CI 提交。

> 注意：`data/seed/reports-2026-06-14/` 不含 `composite_data.json`、`grand_unified.json`，
> 所以全新 clone 只能直接跑 CI 路徑（`ci_update`）；其餘分析需先跑一次完整更新產生資料。

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
- 來源：`analyzers/composite_score.py` 計算財務複合分（0–100）
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
python run.py full_market_crawl

# 2. 法人買賣超
python run.py institutional_flows

# 3. K 線資料（Yahoo Finance，無速率限制）
python run.py crawl_ohlcv

# 4. 計算分析
python run.py composite_score
python run.py grand_unified
python run.py dna_full_market

# 5. 建置並推送
python run.py auto_push         # 內含 build_dashboard
```

### 快速價格更新（不需全量爬取）

```bash
python run.py daily_refresh    # 僅更新價格+動能
python run.py auto_push        # 內含 build_dashboard
```

### CI 每日更新（GitHub Actions，平日 16:00）

```bash
python run.py ci_update --dry-run    # 本機完整跑一次 CI 流程但不寫檔
python run.py ci_update              # 與 Actions 完全相同的指令
```

### 備份

```bash
python run.py push_key_files   # 推送當日關鍵報告 JSON 至 GitHub（需 $GITHUB_PAT）
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
