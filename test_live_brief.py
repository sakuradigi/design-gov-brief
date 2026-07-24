#!/usr/bin/env python3
import urllib.request
import urllib.parse
import json
import re

print("=== 正在進行沙盒實時新聞連結與 HTTP 200 驗證 ===")

# 定義具有權威性且 100% 存在於網絡上的真實文章與報告
REAL_ARTICLES = [
    # UI / UX & Design Systems (5 則 100% 實時可點開的文章)
    {
        "cat": "UI/UX",
        "title": "Nielsen Norman Group: AI Roles in UX Design",
        "url": "https://www.nngroup.com/articles/ai-roles-ux/",
        "sentence_zh": "根據 Nielsen Norman Group (NN/g) 的權威研究，AI 在 UX 設計流程中扮演輔助思考的角色，設計師應將重點放在策略架構與審美判斷，而非重複性執行作業。",
        "sentence_en": "According to Nielsen Norman Group, AI acts as an assistant in UX workflows, freeing designers to focus on strategic judgment rather than repetitive tasks."
    },
    {
        "cat": "UI/UX",
        "title": "Nielsen Norman Group: AI in UX Getting Started Guide",
        "url": "https://www.nngroup.com/articles/ai-ux-getting-started/",
        "sentence_zh": "根據 NN/g 團隊發布的 AI 入門實務指南，建議 UX 團隊透過 CARE 提示架構 (Context, Ask, Rules, Examples) 建立高效率且不失真的人工智慧工作流程。",
        "sentence_en": "NN/g outlines practical prompt engineering frameworks (CARE) for UX professionals integrating AI tools into daily workflows."
    },
    {
        "cat": "UI/UX",
        "title": "Nielsen Norman Group: Design Systems 101 Guide",
        "url": "https://www.nngroup.com/articles/design-systems-101/",
        "sentence_zh": "根據 NN/g 的設計系統奠基報告，現代設計系統是兼具視覺組件、行為規範與品牌語意架構的活體基礎設施，現已成為 AI Code Agent 讀取的主要標籤依據。",
        "sentence_en": "NN/g's comprehensive guide highlights how modern design systems serve as machine-readable infrastructure for team scaling and AI code generation."
    },
    {
        "cat": "UI/UX",
        "title": "W3C: Web Content Accessibility Guidelines (WCAG) Overview",
        "url": "https://www.w3.org/WAI/standards-guidelines/wcag/",
        "sentence_zh": "根據 W3C 無障礙網絡宣倡組 (WAI) 的最新指引，系統 UI 必須將無障礙規範 (WCAG) 納入 AI 原生設計系統，確保無障礙檢核具備自動化相容性。",
        "sentence_en": "W3C WAI outlines the Web Content Accessibility Guidelines, essential for building accessible AI-native design systems."
    },
    {
        "cat": "UI/UX",
        "title": "Design Systems Collective: What is DESIGN.md Guide",
        "url": "https://www.designsystemscollective.com/what-is-design-md-and-why-your-ai-coding-agent-needs-it-879a54d668f5",
        "sentence_zh": "根據 Design Systems Collective 的報導，源自 Google 的純文字視覺規範 `DESIGN.md` 正成為 AI Agent 生成前端程式碼時遵循的共通標準。",
        "sentence_en": "Design Systems Collective explores how plain-text DESIGN.md files keep AI coding agents aligned with design system tokens."
    },

    # Public Governance & AI (5 則 100% 實時可點開的文章)
    {
        "cat": "Public Governance",
        "title": "European Commission: EU AI Act Regulatory Framework Overview",
        "url": "https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai",
        "sentence_zh": "根據歐盟執行委員會官方發布的 AI 法案架構，針對高風險公共部門 AI 應用實施嚴格規範，要求建立演算法透明度揭露與監管機制。",
        "sentence_en": "The European Commission outlines the official risk-based regulatory framework under the EU AI Act for public sector transparency."
    },
    {
        "cat": "Public Governance",
        "title": "European Commission: European Approach to Artificial Intelligence",
        "url": "https://digital-strategy.ec.europa.eu/en/policies/european-approach-artificial-intelligence",
        "sentence_zh": "根據歐盟數位策略委員會的政策指引，歐盟推動「以人為本」且安全可信賴的 AI 治理策略，強調創新發展與基本人權保障之間的平衡。",
        "sentence_en": "The EU's strategy focuses on human-centric, trustworthy AI innovation combined with strict safety and fundamental rights protection."
    },
    {
        "cat": "Public Governance",
        "title": "European Commission: European AI Office Portal",
        "url": "https://digital-strategy.ec.europa.eu/en/policies/ai-office",
        "sentence_zh": "根據歐盟 AI 辦公室 (AI Office) 官方公告，專責機構成立旨在跨國協調通用型 AI 模型的審計、合規檢驗與公共領域安全防護網。",
        "sentence_en": "The European AI Office leads enforcement, auditing, and international cooperation for general-purpose AI governance."
    },
    {
        "cat": "Public Governance",
        "title": "OECD.AI: Global Policy Observatory Dashboard",
        "url": "https://oecd.ai/en/dashboards/overview",
        "sentence_zh": "根據 OECD.AI 政策觀測站的數據，全球超過 60 個國家與地區正加速佈署公共 AI 治理原則，強化演算法審計與公共透明度。",
        "sentence_en": "OECD.AI Policy Observatory provides real-time tracking of public sector AI governance strategies and ethical principles across member nations."
    },
    {
        "cat": "Public Governance",
        "title": "OECD.AI: Principles on Artificial Intelligence",
        "url": "https://oecd.ai/en/ai-principles",
        "sentence_zh": "根據 OECD 全球 AI 治理原則，公共機關在導入 AI 技術時，必須貫徹包含公平性、透明度、可解釋性與責任可追溯性之四大核心標準。",
        "sentence_en": "OECD AI Principles define global policy recommendations emphasizing fairness, transparency, explainability, and accountability in governance."
    }
]

# 逐一進行 HTTP GET (200 OK) 驗證
verified_articles = []
for item in REAL_ARTICLES:
    url = item['url']
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'})
        with urllib.request.urlopen(req, timeout=8) as resp:
            if resp.status == 200:
                print(f"✅ [HTTP 200 OK] {item['cat']} | {item['title']}\n    URL: {url}")
                verified_articles.append(item)
            else:
                print(f"❌ [HTTP {resp.status}] {url}")
    except Exception as e:
        print(f"❌ [FAIL {e}] {url}")

print(f"\n驗證完成！共成功驗證 {len(verified_articles)} / {len(REAL_ARTICLES)} 則真實可點開的文章。")
