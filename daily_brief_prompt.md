# Antigravity 每日設計與 AI 治理日報生成任務 Prompt

> **任務目標**：每天早上 08:00，由 Antigravity 自動進行網路檢索，精選出「設計界與 UI/UX 前沿 5 則」以及「政府治理與 AI 協助治理 5 則」（共 10 則），來自 **10 個完全不同且具備廣度的全球權威機構與媒體**，生成可調整字體、雙語切換且寬屏美觀的 HTML 簡報。

---

## 1. 定時執行規範 (Schedule Specification)
- **執行時間**：每日 08:00 (Asia/Taipei)
- **輸出檔案路徑**：`briefs/morning_brief_YYYY-MM-DD.html`
- **歸檔更新**：執行 `python3 generate_daily_brief.py` 更新 `index.html` 歸檔頁面

---

## 2. 🌐 來源多樣性與廣度硬性規範 (Diverse Sources & Breadth Rules)

> 🚨 **10 則新聞必須來自 10 個完全不同的獨立機構與網域 (Domains)！**
> 絕對禁止將來源侷限於單一網站（例如全部來自同一媒體），必須廣泛涵蓋國際研究機構、標準組織、政府數位部門與權威設計媒體：

### 🎨 UI / UX 推薦多樣來源庫（選擇 5 個不重複網域）：
1. **Nielsen Norman Group (nngroup.com)** — 人機互動與 UX 實證研究
2. **W3C WAI (w3.org)** — 國際 Web 標準與 WCAG 無障礙規範
3. **Design Systems Collective (designsystemscollective.com)** — 設計系統與 DESIGN.md 規範
4. **ACM CHI Conference (chi2026.acm.org)** — 全球人機互動頂級學術大會
5. **Figma Developer Portal (figma.com)** — 開放 Design Tokens 與 API 技術門戶
6. **Smashing Magazine (smashingmagazine.com)** — 前端與 UI 架構媒體

### 🏛️ 公共治理與 AI 推薦多樣來源庫（選擇 5 個不重複網域）：
1. **European Commission (digital-strategy.ec.europa.eu)** — 歐盟 AI 法規與數位策略
2. **OECD.AI Policy Observatory (oecd.ai)** — OECD 全球 AI 治理觀測站
3. **GovTech Singapore (tech.gov.sg)** — 新加坡智慧國家數位政府團隊
4. **Digital.gov (digital.gov)** — 美國聯邦數位服務與 UX 指引
5. **Nesta UK (nesta.org.uk)** — 英國國家公共創新基金會
6. **World Economic Forum (weforum.org)** — 全球經濟論壇 AI 治理聯盟

---

## 3. ⚠️ 深度文章連結硬性規定 (Critical Deep Link Requirement)

> 每次檢索到的新聞與報告，**連結 `href="..."` 必須為該篇專文或報告的「實時有效 200 OK 網址」**，確保點擊標題能直接開啟該篇原文閱讀！

---

## 4. 網頁版面與雙語 DOM 規範

請依照 `templates/brief_template.html` 結構輸出 HTML：
- **容器寬度**：`max-width: 1140px;`（電腦大螢幕寬闊舒服，同時支援 RWD 手機/BOOX 閱覽）。
- **工具列功能**：包含字體縮放按鈕 (`A-` / `標準` / `A+`) 與語言切換按鈕 (`中英` / `繁中` / `EN`)。

每筆新聞條目格式：
```html
<div class="item">
  <div class="item-num">1</div>
  <div class="item-body">
    <div class="item-title">
      <a href="精準文章完整URL" target="_blank" rel="noopener">機構名稱: 完整文章標題 (Full Article Title)</a>
    </div>
    <div class="item-sentence lang-zh-only">繁體中文摘要，並標註<a class="src" href="精準文章完整URL" target="_blank" rel="noopener">來源專文</a>。</div>
    <footer class="page-footer">
      <div class="meta-item">
        <span>🤖 生成模型：</span>
        <span class="meta-pill">Gemini 3.6 Flash / Antigravity Agent</span>
      </div>
      <div class="meta-item">
        <span>⏱️ 生成時間戳記：</span>
        <span class="meta-pill">YYYY-MM-DD HH:MM:SS (Asia/Taipei)（請動態帶入實際發起生成當下的秒級時間）</span>
      </div>
    </footer>
    <div class="item-sentence-en lang-en-only">English summary sentence with <a class="src" href="精準文章完整URL" target="_blank" rel="noopener">Source Article</a>.</div>
  </div>
</div>
```
