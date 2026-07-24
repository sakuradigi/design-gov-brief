# Antigravity 每日設計與 AI 治理日報生成任務 Prompt

> **任務目標**：每天早上 08:00，由 Antigravity 自動進行網路檢索，精選出「設計界與 UI/UX 前沿 5 則」以及「政府治理與 AI 協助治理 5 則」（共 10 則），來自 **10 個完全不同且具備廣度的全球權威機構與媒體**。
>
> 💡 **核心價值要求**：摘要**絕對禁止寫成平鋪直敘的「本篇文章介紹了...」**，必須提煉該文章的**「高價值戰略洞見 (Core Strategic Insights)」**，說明該趨勢對設計實務、技術架構或公共政策的深層影響與啟示！

---

## 1. 定時執行規範 (Schedule Specification)
- **執行時間**：每日 08:00 (Asia/Taipei)
- **輸出檔案路徑**：`briefs/morning_brief_YYYY-MM-DD.html`
- **歸檔更新**：執行 `python3 generate_daily_brief.py` 更新 `index.html` 歸檔頁面

---

## 2. 💡 摘要洞見規範 (High-Value Insight Summary Rules)

> 🚨 **摘要必須包含「核心洞見」標籤與實質戰略提煉！**

### 正確洞見摘要寫法範例：
- ❌ **錯誤寫法 (平鋪直敘無洞見)**：「根據 NN/g 的報導，這篇文章介紹了 AI 在 UX 設計流程中的各種應用與工具。」
- ✅ **正確洞見寫法 (體現 AI 提煉價值)**：「<span class="insight-tag">核心洞見</span> UX 工作流正從『視覺交接 (Handoff)』全面演進為『意圖與 Agent 編排 (Orchestration)』。NN/g 實證指出，AI 能承擔 70% 的重複性圖稿作業，將設計師價值提升至品牌精神審核、責任 AI 護欄與戰略脈絡設定。」

---

## 3. 🌐 來源多樣性與廣度規範 (10 獨立網域)

> 🚨 **10 則新聞必須來自 10 個完全不同的獨立機構與網域 (Domains)！**

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

## 4. ⚠️ 深度文章連結硬性規定 (Critical Deep Link Requirement)

> 每次檢索到的新聞與報告，**連結 `href="..."` 必須為該篇專文或報告的「實時有效 200 OK 網址」**，確保點擊標題能直接開啟該篇原文閱讀！

---

## 5. 網頁版面與雙語 DOM 規範

每筆新聞條目格式：
```html
<div class="item">
  <div class="item-num">1</div>
  <div class="item-body">
    <div class="item-title">
      <a href="精準文章完整URL" target="_blank" rel="noopener">機構名稱: 完整文章標題 (Full Article Title)</a>
    </div>
    <div class="item-sentence lang-zh-only">
      <span class="insight-tag">核心洞見</span>提煉文章的實質戰略洞見與影響，並標註<a class="src" href="精準文章完整URL" target="_blank" rel="noopener">來源專文</a>。
    </div>
    <div class="item-sentence-en lang-en-only">
      <span class="insight-tag">Core Insight</span>Extract key strategic takeaway, referencing <a class="src" href="精準文章完整URL" target="_blank" rel="noopener">Source Article</a>.
    </div>
  </div>
</div>
```
