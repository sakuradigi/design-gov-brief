# Antigravity 每日設計與 AI 治理日報生成任務 Prompt

> **任務目標**：每天早上 08:00，由 Antigravity 自動進行全網檢索，精選出「視覺藝術、平面動態與 UI/UX 美學 5 則」以及「全球公共治理、政治性實驗與社會創新 5 則」（共 10 則）。
>
> 💡 **主題比例與美學價值要求**：
> 1. **AI 議題比例控管**：每天兩大領域中，**AI 相關議題各佔 2 ~ 3 則為上限**，絕對不畫地自限只寫 AI！
> 2. **🎨 設計與美學板塊**：加入平面設計趨勢 (Graphic Design)、動態設計 (Motion Design)、藝術美學與視覺鑑賞，**必須附帶精選美學圖片展示 (Visual Images)**，協助讀者提升美學素養！
> 3. **🏛️ 公共治理與社會創新板塊**：廣泛納入政治性實驗 (Civic Experiments)、參與式審議民主、新型治理思維與數位公共基礎設施 (DPI)，用**「白話、好理解的深層洞見」**分享世界正在發生的政策變革！

---

## 1. 定時執行規範 (Schedule Specification)
- **執行時間**：每日 08:00 (Asia/Taipei)
- **輸出檔案路徑**：`briefs/morning_brief_YYYY-MM-DD.html`
- **歸檔更新**：執行 `python3 generate_daily_brief.py` 更新 `index.html` 歸檔頁面

---

## 2. 🎨 主題分類與圖片配圖規範 (Theme Ratios & Media Rules)

### 第一單元：視覺藝術、平面設計趨勢與 UI/UX 美學 (5 則)
- **美學與藝術 (2~3 則)**：平面設計風格（如網格系統、包浩斯、瑞士風）、動態設計 (Motion Graphic)、視覺色彩與字體美學。
  - 📸 **圖片要求**：美學類條目必須附帶 `<img class="item-image" src="..." />` 與圖片說明，展現視覺藝術張力。
- **UI/UX & AI 協作 (2 則)**：AI 原生介面規範、設計系統 Tokens、人機協作分寸。

### 第二單元：全球公共治理、政治性實驗與社會創新 (5 則)
- **政治性實驗與治理思維 (2~3 則)**：參與式審議民主沙盒、數位公共基礎設施 (DPI)、公民參與、公共服務白話化與包容性。
- **AI 治理與公共問責 (2 則)**：演算法審計清冊、人類最終簽核 (Human-in-the-loop)、國家級採購標準。

---

## 3. 🌐 來源多樣性與廣度規範 (10 獨立網域)

> 🚨 **10 則新聞必須來自 10 個完全不同的獨立機構與網域 (Domains)！**

### 🎨 美學與設計推薦多樣來源庫：
1. **Nielsen Norman Group (nngroup.com)** — 人機互動與設計系統研究
2. **W3C WAI (w3.org)** — 國際 Web 標準與 WCAG 包容美學
3. **Design Systems Collective (designsystemscollective.com)** — 設計系統與 DESIGN.md 規範
4. **ACM CHI Conference (chi2026.acm.org)** — 全球人機互動與動態藝術研討會
5. **Figma Developer Portal (figma.com)** — 開放 Design Tokens 與視覺 API

### 🏛️ 公共治理與社會創新推薦多樣來源庫：
1. **Nesta UK (nesta.org.uk)** — 英國國家公共創新基金會與民主實驗
2. **GovTech Singapore (tech.gov.sg)** — 新加坡智慧國家數位政府團隊
3. **Digital.gov (digital.gov)** — 美國聯邦數位服務與公民 UX 指導方針
4. **European Commission (digital-strategy.ec.europa.eu)** — 歐盟數位策略與法規
5. **OECD.AI Policy Observatory (oecd.ai)** — OECD 全球 AI 與公共政策觀測站

---

## 4. ⚠️ 深度文章連結與白話洞見格式

每筆新聞條目格式：
```html
<div class="item">
  <div class="item-num">1</div>
  <div class="item-body">
    <div class="item-title">
      <a href="精準文章完整URL" target="_blank" rel="noopener">主題類別：完整文章標題 (Full Article Title)</a>
    </div>
    <!-- 若為美學/平面/動態條目，附帶精選圖片 -->
    <img class="item-image" src="../assets/images/xxx.jpg" alt="圖片說明">
    <div class="item-image-caption">🖼️ 今日美學選圖：圖片特色說明...</div>
    
    <div class="item-sentence lang-zh-only">
      <span class="aesthetic-tag">美學與藝術</span>（或 <span class="civic-tag">政治性實驗</span> / <span class="insight-tag">白話洞見</span>）用通俗白話提煉深層價值與脈絡，並標註<a class="src" href="精準文章完整URL" target="_blank" rel="noopener">來源專文</a>。
    </div>
    <div class="item-sentence-en lang-en-only">
      <span class="aesthetic-tag">Aesthetics</span> Plain language insight summary in English, referencing <a class="src" href="精準文章完整URL" target="_blank" rel="noopener">Source Article</a>.
    </div>
  </div>
</div>
```
