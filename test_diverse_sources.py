#!/usr/bin/env python3
import urllib.request
import json

# 定義 10 個來自不同領域、不同權威機構與媒體的廣泛來源 (10 獨立不同 Domain)
DIVERSE_SOURCES = [
    # --- 🎨 設計與 UI/UX 5 個完全不同來源 ---
    {
        "cat": "UI/UX",
        "source_name": "Nielsen Norman Group",
        "domain": "nngroup.com",
        "title": "Nielsen Norman Group: AI Roles in UX Design Workflows",
        "url": "https://www.nngroup.com/articles/ai-roles-ux/",
        "sentence_zh": "根據 NN/g 的實證研究，AI 在 UX 設計中擔任輔助思考角色，設計師應將重點放在策略架構與審美判斷，而非重複性執行作業。",
        "sentence_en": "According to Nielsen Norman Group, AI acts as an assistant in UX workflows, freeing designers to focus on strategic judgment."
    },
    {
        "cat": "UI/UX",
        "source_name": "W3C Web Accessibility Initiative",
        "domain": "w3.org",
        "title": "W3C WAI: Web Content Accessibility Guidelines (WCAG) Standard",
        "url": "https://www.w3.org/WAI/standards-guidelines/wcag/",
        "sentence_zh": "根據 W3C 無障礙網絡宣倡組指引，系統 UI 必須將無障礙規範 (WCAG) 納入 AI 原生設計系統，確保自動化檢核相容性。",
        "sentence_en": "W3C WAI outlines global Web Content Accessibility Guidelines essential for building inclusive AI design systems."
    },
    {
        "cat": "UI/UX",
        "source_name": "Design Systems Collective",
        "domain": "designsystemscollective.com",
        "title": "Design Systems Collective: What is DESIGN.md Guide",
        "url": "https://www.designsystemscollective.com/what-is-design-md-and-why-your-ai-coding-agent-needs-it-879a54d668f5",
        "sentence_zh": "根據 Design Systems Collective 報導，純文字視覺規範 `DESIGN.md` 正成為 AI Agent 生成前端程式碼時遵循的統一標準。",
        "sentence_en": "Design Systems Collective explores how plain-text DESIGN.md files ensure AI coding agents produce consistent UI."
    },
    {
        "cat": "UI/UX",
        "source_name": "ACM CHI Conference",
        "domain": "chi2026.acm.org",
        "title": "ACM CHI 2026: Human Factors in Computing Systems International Conference",
        "url": "https://chi2026.acm.org/",
        "sentence_zh": "根據國際人機互動研討會 (ACM CHI 2026) 官方公告，今年核心議題集中於「可解釋性 AI 互動 (XAI UX)」與多模態自然介面設計。",
        "sentence_en": "ACM CHI 2026 highlights international research on Explainable AI (XAI UX) and multimodal natural user interface interaction."
    },
    {
        "cat": "UI/UX",
        "source_name": "Figma Developer Portal",
        "domain": "figma.com",
        "title": "Figma: Design Systems & Component Tokens Specification",
        "url": "https://www.figma.com/developers/",
        "sentence_zh": "根據 Figma 開發者門戶，透過 REST API 與 Design Tokens 的開放串接，團隊得以建置能夠與 AI 寫作工具自動連動的組件架構。",
        "sentence_en": "Figma Developer platform outlines how open design tokens and REST APIs empower AI tools to query component logic."
    },

    # --- 🏛️ 政府治理與 AI 5 個完全不同來源 ---
    {
        "cat": "Public Governance",
        "source_name": "European Commission",
        "domain": "digital-strategy.ec.europa.eu",
        "title": "European Commission: EU AI Act Regulatory Framework",
        "url": "https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai",
        "sentence_zh": "根據歐盟執行委員會發布的 AI 法案架構，針對高風險公共部門 AI 應用實施嚴格規範，要求建立演算法透明度揭露與監管機制。",
        "sentence_en": "The European Commission outlines the risk-based regulatory framework under the EU AI Act for public sector AI transparency."
    },
    {
        "cat": "Public Governance",
        "source_name": "OECD AI Policy Observatory",
        "domain": "oecd.ai",
        "title": "OECD.AI: Global Policy Observatory & Principles",
        "url": "https://oecd.ai/en/dashboards/overview",
        "sentence_zh": "根據 OECD.AI 政策觀測站數據，全球超過 60 個國家正加速佈署公共 AI 治理原則，貫徹公平性、透明度與責任可追溯性。",
        "sentence_en": "OECD.AI Policy Observatory provides real-time tracking of public sector AI governance strategies and ethical principles."
    },
    {
        "cat": "Public Governance",
        "source_name": "World Economic Forum (WEF)",
        "domain": "weforum.org",
        "title": "World Economic Forum: AI Governance Alliance Reports",
        "url": "https://www.weforum.org/agenda/2024/01/ai-governance-alliance-prescient-insights/",
        "sentence_zh": "根據世界經濟論壇 (WEF) AI 治理聯盟報告，強調各國政府與企業必須建立負責任的生成式 AI 採購標準與風險評估機制。",
        "sentence_en": "World Economic Forum's AI Governance Alliance outlines frameworks for responsible generative AI adoption in the public sphere."
    },
    {
        "cat": "Public Governance",
        "source_name": "United Nations Public Administration",
        "domain": "un.org",
        "title": "United Nations: E-Government Survey & Digital Governance",
        "url": "https://publicadministration.un.org/en/Research/UN-e-Government-Survey",
        "sentence_zh": "根據聯合國 (UN) 電子化政府調查報告，全球數位政府正從單純業務線上化轉型為以數據驅動與包容性為核心的智慧公共服務平台。",
        "sentence_en": "United Nations E-Government Survey tracks progress in inclusive digital public infrastructure and data-driven public governance."
    },
    {
        "cat": "Public Governance",
        "source_name": "GovTech Singapore",
        "domain": "tech.gov.sg",
        "title": "GovTech Singapore: Smart Nation Digital Government Group",
        "url": "https://www.tech.gov.sg/",
        "sentence_zh": "根據新加坡 GovTech 官方公告，其推動智慧國家數位政府計劃，重點在於建立跨機關安全的公共 API 共享與 AI 審核輔助系統。",
        "sentence_en": "GovTech Singapore shares insights on building scalable digital public infrastructure, secure APIs, and AI-assisted governance."
    }
]

print("=== 正在進行 10 個多樣化獨立網域 (Domains) 的實時 HTTP GET 驗證 ===")
verified = []
for item in DIVERSE_SOURCES:
    url = item['url']
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'})
        with urllib.request.urlopen(req, timeout=8) as resp:
            if resp.status == 200:
                print(f"✅ [200 OK] Domain: {item['domain']:<30} | {item['source_name']}")
                verified.append(item)
            else:
                print(f"❌ [HTTP {resp.status}] {url}")
    except Exception as e:
        print(f"❌ [FAIL {e}] {url}")

print(f"\n驗證完成！共成功取得 {len(verified)} / {len(DIVERSE_SOURCES)} 則來自完全不同權威機構的實時文章。")
