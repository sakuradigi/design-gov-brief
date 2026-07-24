# Antigravity 每日設計與 AI 治理日報生成任務 Prompt

> **任務目標**：每天早上 08:00，由 Antigravity 自動進行網路檢索，精選出「設計界與 UI/UX 前沿 5 則」以及「政府治理與 AI 協助治理 5 則」（共 10 則），生成可調整字體、雙語切換且寬屏美觀的 HTML 簡報。

---

## 1. 定時執行規範 (Schedule Specification)
- **執行時間**：每日 08:00 (Asia/Taipei)
- **輸出檔案路徑**：`briefs/morning_brief_YYYY-MM-DD.html`
- **歸檔更新**：執行 `python3 generate_daily_brief.py` 更新 `index.html` 歸檔頁面

---

## 2. ⚠️ 深度文章連結硬性規定 (Critical Deep Link Requirement)

> 🚨 **絕對禁止只填寫首頁網址（如 `https://uxdesign.cc` 或 `https://oecd.org`）！**
> 每次檢索到的新聞與報告，**連結 `href="..."` 必須為該篇深度文章或報告的「完整直接 URL」**（例如：`https://uxdesign.cc/mapping-ai-presence-to-user-intent-76b6680caae2`），確保點擊標題能直接打開該篇原文閱讀！

---

## 3. 檢索主題與數量要求 (Search & Quantity Specifications)

1. **🎨 每日設計新聞與 UI/UX 前沿 (Design & UI/UX)** — **精選 5 則**
   - 關鍵字：`UI UX design trends 2026`, `Design Systems Collective`, `Figma updates`, `Nielsen Norman Group UX`, `AI design tools`, `Agentic UX`
   - 焦點：AI Agent 介面規範（如 `DESIGN.md`）、設計系統演進、微互動、GenUI、多模態體驗。

2. **🏛️ 政府治理與 AI 協助治理 (Government Governance & Public AI)** — **精選 5 則**
   - 關鍵字：`GovTech innovation`, `digital government policy`, `public service design`, `OECD public governance`, `AI in public sector`, `EU AI Act public`
   - 焦點：數位政府創新、智慧城市治理、公共服務 UI/UX 重構、AI 審核公文/法規、演算法透明度與護欄。

3. **💡 每日中英格言 (Daily Quote)**
   - 挑選一對精闢的設計或治理領域名人金句，提供英文原文 (`QUOTE_EN`)、繁體中文翻譯 (`QUOTE_ZH`) 與作者來源 (`QUOTE_AUTHOR`)。

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
      <a href="精準文章完整URL" target="_blank" rel="noopener">完整文章標題 (Full Article Title)</a>
    </div>
    <div class="item-sentence lang-zh-only">繁體中文摘要，並標註<a class="src" href="精準文章完整URL" target="_blank" rel="noopener">來源專文</a>。</div>
    <div class="item-sentence-en lang-en-only">English summary sentence with <a class="src" href="精準文章完整URL" target="_blank" rel="noopener">Source Article</a>.</div>
  </div>
</div>
```
