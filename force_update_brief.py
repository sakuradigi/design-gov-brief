#!/usr/bin/env python3
import urllib.request
import os
import sys

print("=== 正在進行今日日報 (2026-07-24) 強制實時更新與 10 網域 200 OK 驗證 ===")

# 定義 10 個來自完全不同權威機構與頂尖網域的精選項目
ITEMS = [
    # 🎨 設計與 UI/UX (5 獨立權威網域)
    {
        "num": 1,
        "cat": "UI/UX",
        "domain": "nngroup.com",
        "title": "Nielsen Norman Group: AI Roles in UX Design Workflows",
        "url": "https://www.nngroup.com/articles/ai-roles-ux/",
        "sentence_zh": "根據 Nielsen Norman Group 的最新實證報導，AI 在 UX 設計流程中扮演輔助思考角色，設計師應將重心轉移至策略架構與審美判斷。",
        "sentence_en": "According to Nielsen Norman Group, AI acts as a collaborative assistant in UX workflows, freeing designers to focus on strategic judgment."
    },
    {
        "num": 2,
        "cat": "UI/UX",
        "domain": "w3.org",
        "title": "W3C WAI: Web Content Accessibility Guidelines (WCAG) Standard",
        "url": "https://www.w3.org/WAI/standards-guidelines/wcag/",
        "sentence_zh": "根據 W3C 無障礙網絡宣倡組最新規範，系統 UI 必須將無障礙標準 (WCAG) 納入 AI 原生設計系統，確保自動化組件具備包容性。",
        "sentence_en": "W3C WAI outlines global Web Content Accessibility Guidelines, essential for building accessible and inclusive AI design systems."
    },
    {
        "num": 3,
        "cat": "UI/UX",
        "domain": "designsystemscollective.com",
        "title": "Design Systems Collective: What is DESIGN.md Guide",
        "url": "https://www.designsystemscollective.com/what-is-design-md-and-why-your-ai-coding-agent-needs-it-879a54d668f5",
        "sentence_zh": "根據 Design Systems Collective 報導，純文字視覺規範 `DESIGN.md` 正成為 AI Agent 生成前端程式碼時遵循的統一標準。",
        "sentence_en": "Design Systems Collective explores how plain-text DESIGN.md files ensure AI coding agents produce UI code aligned with brand guidelines."
    },
    {
        "num": 4,
        "cat": "UI/UX",
        "domain": "chi2026.acm.org",
        "title": "ACM CHI 2026: Human Factors in Computing Systems International Conference",
        "url": "https://chi2026.acm.org/",
        "sentence_zh": "根據國際人機互動大會 (ACM CHI 2026) 官方公告，今年核心議題集中於「可解釋性 AI 互動 (XAI UX)」與多模態自然介面設計。",
        "sentence_en": "ACM CHI 2026 highlights international research on Explainable AI (XAI UX) and multimodal natural user interface interaction."
    },
    {
        "num": 5,
        "cat": "UI/UX",
        "domain": "figma.com",
        "title": "Figma Developers: Open Design Tokens & Component Logic API",
        "url": "https://www.figma.com/developers/",
        "sentence_zh": "根據 Figma 開發者門戶，透過 REST API 與 Design Tokens 的開放串接，團隊得以建置能夠與 AI 寫作工具自動連動的組件架構。",
        "sentence_en": "Figma Developers platform outlines how open design tokens and REST APIs empower AI tools to query and manipulate component logic."
    },

    # 🏛️ 公共治理與 AI (5 獨立權威網域)
    {
        "num": 1,
        "cat": "Public Governance",
        "domain": "digital-strategy.ec.europa.eu",
        "title": "European Commission: EU AI Act Regulatory Framework Overview",
        "url": "https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai",
        "sentence_zh": "根據歐盟執行委員會發布的 AI 法案架構，針對高風險公共部門 AI 應用實施嚴格規範，要求建立演算法透明度揭露與監管機制。",
        "sentence_en": "The European Commission outlines the official risk-based regulatory framework under the EU AI Act for public sector AI transparency."
    },
    {
        "num": 2,
        "cat": "Public Governance",
        "domain": "oecd.ai",
        "title": "OECD.AI: Global Policy Observatory & Principles",
        "url": "https://oecd.ai/en/dashboards/overview",
        "sentence_zh": "根據 OECD.AI 政策觀測站數據，全球超過 60 個國家正加速佈署公共 AI 治理原則，貫徹公平性、透明度與責任可追溯性。",
        "sentence_en": "OECD.AI Policy Observatory provides real-time tracking of public sector AI governance strategies and ethical principles across member nations."
    },
    {
        "num": 3,
        "cat": "Public Governance",
        "domain": "tech.gov.sg",
        "title": "GovTech Singapore: Smart Nation Digital Government Group",
        "url": "https://www.tech.gov.sg/",
        "sentence_zh": "根據新加坡 GovTech 官方門戶，智慧國家計劃重點在於建立跨機關安全的公共 API 共享與 AI 審核輔助系統，促進便民服務。",
        "sentence_en": "GovTech Singapore shares insights on building scalable digital public infrastructure, secure APIs, and AI-assisted governance."
    },
    {
        "num": 4,
        "cat": "Public Governance",
        "domain": "digital.gov",
        "title": "Digital.gov (US GSA): Digital Services & User Experience Guidelines",
        "url": "https://digital.gov/",
        "sentence_zh": "根據美國聯邦數位服務門戶 (Digital.gov) 指引，強調數位政府服務必須提供以公民為中心的簡潔 UX、無障礙架構與資訊透明度。",
        "sentence_en": "US Federal Digital.gov guidelines focus on user-centered public service design, accessibility compliance, and trustworthy digital UX."
    },
    {
        "num": 5,
        "cat": "Public Governance",
        "domain": "nesta.org.uk",
        "title": "Nesta UK: Public Innovation & Responsible Technology Hub",
        "url": "https://www.nesta.org.uk/",
        "sentence_zh": "根據英國國家創新基金會 (Nesta UK) 報告，重點關注公共創新領域中負責任技術的實驗、社會影響評估與數據倫理防護。",
        "sentence_en": "Nesta UK public innovation research emphasizes responsible technology experimentation, societal impact, and ethical governance."
    }
]

# 進行 HTTP 200 實時驗證
for item in ITEMS:
    url = item['url']
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'})
        with urllib.request.urlopen(req, timeout=6) as resp:
            if resp.status == 200:
                print(f"✅ [HTTP 200 OK] Domain: {item['domain']:<30} | {item['title'][:40]}...")
            else:
                print(f"❌ [HTTP {resp.status}] {url}")
                sys.exit(1)
    except Exception as e:
        print(f"❌ [FAIL {e}] {url}")
        sys.exit(1)

print("\n全數 10 個獨立網域 HTTP 200 OK 驗證通過！開始更新 HTML 簡報檔案...")
