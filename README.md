# 🏛️ 🎨 設計與治理日報 (Design & Governance Daily Brief)

![banner](assets/og_image.jpg)

這是一個每日自動化整理「設計美學、UI/UX 趨勢」與「公共治理、社會創新、數位政府」的高品質開源日報系統。本專案結合了 RSS 自動爬蟲與 **Google Gemini 3.6 Flash** 大型語言模型，不僅僅是翻譯新聞，更能深度提煉出每一件時事背後的「趨勢意義與洞見」。

文體設定為「懂設計與治理的好朋友，在晨間咖啡時間與讀者交流深度觀點」，讓冰冷的新聞轉化為溫暖而具啟發性的洞察。

🌐 **線上閱讀**：[https://sakuradigi.github.io/design-gov-brief](https://sakuradigi.github.io/design-gov-brief)

---

## ✨ 專案特色 (Features)

1. **嚴選高品質 RSS 來源**
   摒棄內容農場與純粹硬體評測，嚴選如 *UX Collective*, *Smashing Magazine*, *The GovLab* 等高質量設計與治理智庫，以及各國的主流深度新聞媒體。
2. **深度洞見摘要 (Deep Insights)**
   使用最新 Gemini 模型進行分析，拒絕生硬翻譯或公文套話。以「白話、通俗、精闢」的文體指出事件「為什麼重要 (Why it matters)」。
3. **區域新聞配額制 (Regional Quota)**
   確保每天的治理創新新聞具備全球視野，自動配置精準比例：
   - 治理專區：**1 篇台灣、1 篇歐洲、1 篇北美、1 篇日本、1 篇彈性（智庫、國際）**。並特別過濾台灣區中不相關的港澳新聞。
   - 設計專區：包含 **2 篇日系設計（如 JDN、AXIS 等）、3 篇歐美與綜合設計**，兼顧東方細膩美學與西方前沿技術。
4. **自動防業配機制 (Anti-Junk Filter)**
   內建關鍵字過濾器，自動剔除打折、促銷、耳機評測等無關內容，維持報紙高純度的知識含金量。
5. **完全自動化與靜態部署 (Serverless)**
   使用 GitHub Actions 每天早上定時執行爬蟲與生成，產生靜態 HTML 後部署至 GitHub Pages，零伺服器成本。

---

## 🏗️ 運作架構 (Architecture)

1. **GitHub Actions (`daily_brief.yml`)**：每日早上 8:00 (台北時間) 自動觸發。
2. **Python 爬蟲 (`generate_daily_brief.py`)**：拉取 RSS 進行過濾、配額與 HTTP 200 檢查，並擷取各文章的 `og:image` 縮圖。
3. **LLM 洞見萃取**：透過 Gemini API 解析文章，產出大標題、快訊與各篇文章的深度中英雙語洞見。
4. **HTML 渲染與靜態生成**：將結果套用美觀的版型，寫入 `briefs/` 並同步更新 `index.html` 首頁歸檔卡片。
5. **部署至 GitHub Pages**：由 GitHub Actions 無縫完成發布。

---

## 🚀 本地開發 (Local Development)

若您希望在本地測試或調整爬蟲與生成邏輯：

### 1. 安裝依賴
專案主要使用 Python 內建函式庫（如 `xml.etree.ElementTree`、`urllib` 等），僅需安裝 `google-generativeai` 來串接 Gemini API。

```bash
pip install google-generativeai
```

### 2. 設定環境變數
您需要一組 Gemini API Key 才能產出洞察內容：
```bash
export GEMINI_API_KEY="your_api_key_here"
```

### 3. 生成日報
手動觸發日報生成（將爬取 RSS 並呼叫 API 產生今日簡報）：
```bash
python generate_daily_brief.py
```

如果你只想要更新首頁 `index.html` 上的歷史歸檔卡片（不重新打 API 爬文）：
```bash
python generate_daily_brief.py --update-index-only
```
如果想測試抓取與過濾邏輯但不呼叫 Gemini：
```bash
python generate_daily_brief.py --skip-gemini
```

---

## 📝 審計與除錯 (Auditing & Debugging)

專案內建強大的審計機制，每次生成都會在 `audit/` 資料夾下產生 `audit_YYYY-MM-DD.json`。該檔案詳細記錄了：
- 成功抓取的文章總數
- HTTP 可訪問性驗證結果
- 每一篇文章的區域標籤 (Region) 與來源 (Source)
可幫助開發者快速釐清為何特定文章被選中或排除。

---

## 📜 授權與宣告 (License & Disclaimer)

- 本專案程式碼開源，歡迎 Fork 與改良。
- 專案內爬取的文章版權歸原出處（RSS 來源網站）所有，日報僅作摘要、洞見分析與超連結導流，不做任何全文轉載與商業用途。
- 本專案採用 MIT License。
