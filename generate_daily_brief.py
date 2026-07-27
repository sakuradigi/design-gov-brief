#!/usr/bin/env python3
"""
設計、治理日報 — 每日自動生成腳本
核心原則：「先爬後寫」— RSS 爬取真實文章 → HTTP 驗證 → og:image 擷取 → LLM 白話摘要 → 填入模板
LLM 絕對不碰任何 URL。所有連結來自 RSS feed。
"""
import os
import re
import sys
import glob
import json
import html
import hashlib
import argparse
import traceback
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from urllib.parse import urlparse, urljoin

# === 路徑設定 ===
WORKSPACE_DIR = os.path.dirname(os.path.abspath(__file__))
BRIEFS_DIR = os.path.join(WORKSPACE_DIR, 'briefs')
INDEX_PATH = os.path.join(WORKSPACE_DIR, 'index.html')
TEMPLATE_PATH = os.path.join(WORKSPACE_DIR, 'templates', 'brief_template.html')
AUDIT_DIR = os.path.join(WORKSPACE_DIR, 'audit')

# === HTTP 設定 ===
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9,zh-TW;q=0.8',
}

# === RSS 來源設定 ===
# 每個 feed 包含: url, category ('design' | 'gov'), source_name
RSS_FEEDS = [
    # 🎨 設計類
    {
        'url': 'https://www.itsnicethat.com/rss/all',
        'category': 'design',
        'source_name': "It's Nice That",
    },
    {
        'url': 'https://www.dezeen.com/feed/',
        'category': 'design',
        'source_name': 'Dezeen',
    },
    {
        'url': 'https://www.creativebloq.com/feed',
        'category': 'design',
        'source_name': 'Creative Bloq',
    },
    {
        'url': 'https://www.smashingmagazine.com/feed/',
        'category': 'design',
        'source_name': 'Smashing Magazine',
    },
    {
        'url': 'https://eyeondesign.aiga.org/feed/',
        'category': 'design',
        'source_name': 'AIGA Eye on Design',
    },
    {
        'url': 'https://www.designweek.co.uk/feed/',
        'category': 'design',
        'source_name': 'Design Week',
    },
    # 🏛️ 治理類
    {
        'url': 'https://news.google.com/rss/search?q=digital+governance+OR+civic+tech+OR+public+innovation+OR+AI+regulation&hl=en&gl=US&ceid=US:en',
        'category': 'gov',
        'source_name': 'Google News (Gov/Civic Tech EN)',
    },
    {
        'url': 'https://news.google.com/rss/search?q=%E6%95%B8%E4%BD%8D%E6%B2%BB%E7%90%86+OR+AI%E6%B2%BB%E7%90%86+OR+%E6%99%BA%E6%85%A7%E5%9F%8E%E5%B8%82+OR+%E9%96%8B%E6%94%BE%E6%94%BF%E5%BA%9C&hl=zh-TW&gl=TW&ceid=TW:zh-Hant',
        'category': 'gov',
        'source_name': 'Google News (數位治理 TW)',
    },
    {
        'url': 'https://www.govtech.com/rss',
        'category': 'gov',
        'source_name': 'GovTech',
    },
    {
        'url': 'https://thegovlab.org/feed',
        'category': 'gov',
        'source_name': 'The GovLab',
    },
]

# === 文章數量設定 ===
TARGET_DESIGN_ARTICLES = 5
TARGET_GOV_ARTICLES = 5
MAX_ARTICLE_AGE_DAYS = 7  # 只收最近 7 天的文章


# ──────────────────────────────────────────────
# 1. RSS 爬取模組
# ──────────────────────────────────────────────

def fetch_url(url, timeout=10):
    """安全的 HTTP GET，回傳 (status_code, content_bytes) 或 (None, None)"""
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.getcode(), resp.read()
    except urllib.error.HTTPError as e:
        print(f"  ⚠ HTTP {e.code} for {url}")
        return e.code, None
    except Exception as e:
        print(f"  ⚠ Fetch error for {url}: {e}")
        return None, None


def parse_rss_feed(feed_url, source_name, category):
    """解析 RSS/Atom feed，回傳文章列表"""
    print(f"📡 Fetching feed: {source_name} ({feed_url[:80]}...)")
    status, content = fetch_url(feed_url, timeout=15)
    if status != 200 or content is None:
        print(f"  ❌ Feed unavailable (status={status})")
        return []

    articles = []
    try:
        # 移除 XML namespace 以簡化解析
        content_str = content.decode('utf-8', errors='ignore')
        # Strip namespaces for easier parsing
        content_str = re.sub(r'\sxmlns[^"]*"[^"]*"', '', content_str)
        content_str = re.sub(r'<(/?)(\w+):', r'<\1', content_str)

        root = ET.fromstring(content_str)

        # 嘗試 RSS 2.0 格式
        items = root.findall('.//item')
        if not items:
            # 嘗試 Atom 格式
            items = root.findall('.//entry')

        cutoff_date = datetime.now(timezone.utc) - timedelta(days=MAX_ARTICLE_AGE_DAYS)

        for item in items:
            article = extract_article_from_item(item, source_name, category, cutoff_date)
            if article:
                articles.append(article)

    except ET.ParseError as e:
        print(f"  ❌ XML parse error: {e}")
    except Exception as e:
        print(f"  ❌ Unexpected error parsing feed: {e}")
        traceback.print_exc()

    print(f"  ✅ Found {len(articles)} recent articles from {source_name}")
    return articles


def extract_article_from_item(item, source_name, category, cutoff_date):
    """從 RSS item 中提取文章資訊"""
    # 取得標題
    title_el = item.find('title')
    if title_el is None or not title_el.text:
        return None
    title = html.unescape(title_el.text.strip())

    # 取得連結
    link = None
    link_el = item.find('link')
    if link_el is not None:
        link = link_el.text if link_el.text else link_el.get('href')
    if not link:
        # Atom format
        for l in item.findall('link'):
            href = l.get('href')
            if href:
                link = href
                break
    if not link:
        return None
    link = link.strip()

    # 取得發布日期
    pub_date = None
    for date_tag in ['pubDate', 'published', 'updated', 'date']:
        date_el = item.find(date_tag)
        if date_el is not None and date_el.text:
            pub_date = parse_date(date_el.text.strip())
            break

    # 若有日期，檢查是否在有效期限內
    if pub_date and pub_date < cutoff_date:
        return None

    # 取得描述/摘要
    description = ''
    for desc_tag in ['description', 'summary', 'content', 'encoded']:
        desc_el = item.find(desc_tag)
        if desc_el is not None and desc_el.text:
            # 去除 HTML 標籤，取純文字
            raw = desc_el.text
            description = re.sub(r'<[^>]+>', '', raw).strip()
            description = html.unescape(description)
            # 限制長度
            if len(description) > 500:
                description = description[:497] + '...'
            break

    # 嘗試從 description HTML 中抓圖片
    image_from_desc = None
    for desc_tag in ['description', 'summary', 'content', 'encoded']:
        desc_el = item.find(desc_tag)
        if desc_el is not None and desc_el.text:
            img_match = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', desc_el.text)
            if img_match:
                image_from_desc = img_match.group(1)
            break

    # 嘗試 media:content 或 enclosure 取圖
    image_from_media = None
    for media_tag in ['thumbnail', 'content']:
        media_el = item.find(media_tag)
        if media_el is not None:
            url_attr = media_el.get('url')
            if url_attr and any(ext in url_attr.lower() for ext in ['.jpg', '.jpeg', '.png', '.webp', '.gif']):
                image_from_media = url_attr
                break
    enclosure = item.find('enclosure')
    if enclosure is not None and not image_from_media:
        enc_type = enclosure.get('type', '')
        if 'image' in enc_type:
            image_from_media = enclosure.get('url')

    return {
        'title': title,
        'url': link,
        'source': source_name,
        'category': category,
        'pub_date': pub_date.isoformat() if pub_date else None,
        'description': description,
        'image_from_feed': image_from_media or image_from_desc,
        'og_image': None,  # 稍後由 fetch_og_image 填入
        'verified': False,
    }


def parse_date(date_str):
    """嘗試解析多種日期格式"""
    formats = [
        '%a, %d %b %Y %H:%M:%S %z',    # RFC 822: Sun, 27 Jul 2026 08:00:00 +0000
        '%a, %d %b %Y %H:%M:%S %Z',    # Sun, 27 Jul 2026 08:00:00 GMT
        '%Y-%m-%dT%H:%M:%S%z',          # ISO 8601: 2026-07-27T08:00:00+00:00
        '%Y-%m-%dT%H:%M:%SZ',           # ISO 8601 UTC: 2026-07-27T08:00:00Z
        '%Y-%m-%d %H:%M:%S',            # 2026-07-27 08:00:00
        '%Y-%m-%d',                      # 2026-07-27
    ]
    for fmt in formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except ValueError:
            continue
    # 最後嘗試：去除多餘空格與括號內容
    cleaned = re.sub(r'\s*\(.*?\)\s*', '', date_str).strip()
    for fmt in formats:
        try:
            dt = datetime.strptime(cleaned, fmt)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except ValueError:
            continue
    return None


# ──────────────────────────────────────────────
# 2. HTTP 驗證 & og:image 擷取模組
# ──────────────────────────────────────────────

def verify_and_enrich_article(article):
    """驗證文章 URL 可達 + 擷取 og:image"""
    url = article['url']
    print(f"  🔗 Verifying: {url[:80]}...")

    status, content = fetch_url(url, timeout=8)
    if status != 200 or content is None:
        print(f"    ❌ HTTP {status}")
        return False

    try:
        page_html = content.decode('utf-8', errors='ignore')
    except Exception:
        page_html = ''

    # 檢查是否為真正的 404 頁面（有些網站回傳 200 但內容是 404）
    lower_html = page_html[:3000].lower()
    if 'page not found' in lower_html or '404 error' in lower_html or 'does not exist' in lower_html:
        print(f"    ❌ Soft 404 detected")
        return False

    # 擷取 og:image
    og_match = re.search(
        r'<meta\s+(?:property|name)=["\']og:image["\']\s+content=["\']([^"\']+)["\']',
        page_html, re.IGNORECASE
    )
    if not og_match:
        og_match = re.search(
            r'<meta\s+content=["\']([^"\']+)["\']\s+(?:property|name)=["\']og:image["\']',
            page_html, re.IGNORECASE
        )
    if og_match:
        og_url = og_match.group(1)
        # 處理相對路徑
        if og_url.startswith('//'):
            og_url = 'https:' + og_url
        elif og_url.startswith('/'):
            parsed = urlparse(url)
            og_url = f"{parsed.scheme}://{parsed.netloc}{og_url}"
        article['og_image'] = og_url
        print(f"    🖼️  og:image found")

    # 嘗試取得真實頁面標題做比對
    title_match = re.search(r'<title[^>]*>([^<]+)</title>', page_html, re.IGNORECASE)
    if title_match:
        page_title = html.unescape(title_match.group(1).strip())
        article['page_title'] = page_title

    article['verified'] = True
    print(f"    ✅ Verified OK")
    return True


# ──────────────────────────────────────────────
# 3. 文章篩選與排序
# ──────────────────────────────────────────────

def select_articles(all_articles):
    """從所有已驗證的文章中，選出最終要用的 5 設計 + 5 治理"""
    design = [a for a in all_articles if a['category'] == 'design' and a['verified']]
    gov = [a for a in all_articles if a['category'] == 'gov' and a['verified']]

    # 按日期排序（最新在前），無日期的放最後
    def sort_key(a):
        if a['pub_date']:
            return a['pub_date']
        return '0000'
    design.sort(key=sort_key, reverse=True)
    gov.sort(key=sort_key, reverse=True)

    # 去重：同一個 domain 最多取 5 篇
    design = dedupe_by_domain(design, max_per_domain=5)
    gov = dedupe_by_domain(gov, max_per_domain=5)

    selected_design = design[:TARGET_DESIGN_ARTICLES]
    selected_gov = gov[:TARGET_GOV_ARTICLES]

    print(f"\n📊 Final selection: {len(selected_design)} design + {len(selected_gov)} governance articles")
    return selected_design, selected_gov


def dedupe_by_domain(articles, max_per_domain=2):
    """同一個 domain 最多取 max_per_domain 篇"""
    domain_count = {}
    result = []
    for a in articles:
        domain = urlparse(a['url']).netloc
        domain_count[domain] = domain_count.get(domain, 0) + 1
        if domain_count[domain] <= max_per_domain:
            result.append(a)
    return result


# ──────────────────────────────────────────────
# 4. LLM 摘要模組 (Gemini API)
# ──────────────────────────────────────────────

def generate_summaries_with_gemini(design_articles, gov_articles, date_str):
    """使用 Gemini API 產出白話摘要、每日大標題與快訊"""
    api_key = os.environ.get('GEMINI_API_KEY', '')
    if not api_key:
        print("⚠ GEMINI_API_KEY not set, using fallback (article descriptions only)")
        return generate_fallback_summaries(design_articles, gov_articles, date_str)

    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash')
    except ImportError:
        print("⚠ google-generativeai not installed, using fallback")
        return generate_fallback_summaries(design_articles, gov_articles, date_str)
    except Exception as e:
        print(f"⚠ Gemini init error: {e}, using fallback")
        return generate_fallback_summaries(design_articles, gov_articles, date_str)

    # 組建文章清單給 LLM
    articles_text = ""
    all_articles = design_articles + gov_articles
    for i, a in enumerate(all_articles, 1):
        cat_label = "設計" if a['category'] == 'design' else "治理"
        articles_text += f"\n--- 第{i}則 [{cat_label}] ---\n"
        articles_text += f"標題: {a['title']}\n"
        articles_text += f"來源: {a['source']}\n"
        articles_text += f"網址: {a['url']}\n"
        if a['description']:
            articles_text += f"原文摘要: {a['description'][:300]}\n"

    prompt = f"""你是一位懂設計、懂治理又超會聊天的「視覺美學與社會創新日報」總編輯。
今天是 {date_str}。

以下是今天從 RSS 爬取到的 {len(all_articles)} 篇真實文章，請你為每篇寫出：
1. 一句繁體中文白話摘要（50-80字，像在跟朋友聊天一樣自然好讀，嚴禁公文體）
2. 一句英文摘要（30-50字）

另外請產出：
3. 一個今日大標題（繁中，20-35字，反映今天最具代表性的 2-3 個議題關鍵字）
4. 三句「今日重點速覽」快訊（繁中，每句 15-25 字，用白話講今天最重要的三件事）
5. 一句每日格言（英文原文 + 繁中翻譯 + 作者，主題跟設計或治理相關）

【文體要求】
- 白話、通俗、精闢、好閱讀
- 像咖啡時間跟懂行的朋友聊天
- 嚴禁「貫徹」「實施嚴格規範」「責任可追溯性」等公文套話
- 嚴禁學術論文腔

【輸出格式】嚴格用以下 JSON 格式回傳，不要加任何其他文字：
{{
  "headline": "今日大標題文字",
  "flash_news": ["快訊1", "快訊2", "快訊3"],
  "quote_en": "英文格言",
  "quote_zh": "繁中格言翻譯",
  "quote_author": "格言作者",
  "articles": [
    {{"index": 1, "summary_zh": "繁中摘要", "summary_en": "English summary"}},
    ...
  ]
}}

以下是今天的文章：
{articles_text}
"""

    try:
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        # 移除可能的 markdown code block
        response_text = re.sub(r'^```(?:json)?\s*', '', response_text)
        response_text = re.sub(r'\s*```$', '', response_text)
        result = json.loads(response_text)
        print("✅ Gemini summaries generated successfully")
        return result
    except json.JSONDecodeError as e:
        print(f"⚠ JSON parse error from Gemini: {e}")
        print(f"  Response text: {response_text[:200]}...")
        return generate_fallback_summaries(design_articles, gov_articles, date_str)
    except Exception as e:
        print(f"⚠ Gemini API error: {e}")
        return generate_fallback_summaries(design_articles, gov_articles, date_str)


def generate_fallback_summaries(design_articles, gov_articles, date_str):
    """無 LLM 時的備用摘要方案：直接用文章的 description"""
    all_articles = design_articles + gov_articles
    articles_summaries = []
    for i, a in enumerate(all_articles, 1):
        desc = a.get('description', '') or a['title']
        articles_summaries.append({
            'index': i,
            'summary_zh': desc[:100] if desc else a['title'],
            'summary_en': a['title'],
        })

    # 從文章標題組合大標題
    keywords = []
    for a in all_articles[:3]:
        words = a['title'].split()[:3]
        keywords.append(' '.join(words))
    headline = f"今日設計與治理精選 · {date_str}"

    return {
        'headline': headline,
        'flash_news': [
            a['title'][:40] for a in all_articles[:3]
        ],
        'quote_en': '"Design is not just what it looks like and feels like. Design is how it works."',
        'quote_zh': '「設計不只是外表和感覺，設計是讓東西好用。」',
        'quote_author': 'Steve Jobs',
        'articles': articles_summaries,
    }


# ──────────────────────────────────────────────
# 5. HTML 生成模組
# ──────────────────────────────────────────────

def generate_brief_html(design_articles, gov_articles, summaries, date_str):
    """讀取模板，填入真實資料，產出完整 HTML"""
    if not os.path.exists(TEMPLATE_PATH):
        print(f"❌ Template not found: {TEMPLATE_PATH}")
        sys.exit(1)

    with open(TEMPLATE_PATH, 'r', encoding='utf-8') as f:
        template = f.read()

    # 基本欄位替換
    now = datetime.now(timezone(timedelta(hours=8)))
    replacements = {
        '{{DATE_STRING}}': date_str,
        '{{HEADLINE}}': html.escape(summaries.get('headline', f'每日設計與治理簡報 · {date_str}')),
        '{{QUOTE_EN}}': html.escape(summaries.get('quote_en', '')),
        '{{QUOTE_ZH}}': html.escape(summaries.get('quote_zh', '')),
        '{{QUOTE_AUTHOR}}': html.escape(summaries.get('quote_author', '')),
        '{{GENERATED_MODEL}}': 'RSS + Gemini 2.0 Flash',
        '{{GENERATION_TIMESTAMP}}': now.strftime('%Y-%m-%d %H:%M:%S (UTC+8)'),
        '{{CALM_LINE}}': '以下為今日從全球設計與治理媒體 RSS 即時爬取、驗證並摘要的文章。',
    }

    for placeholder, value in replacements.items():
        template = template.replace(placeholder, value)

    # 快訊區塊
    flash_items = summaries.get('flash_news', [])
    flash_html = ''
    for item_text in flash_items:
        flash_html += f'        <li class="flash-item">{html.escape(item_text)}</li>\n'
    template = template.replace('{{FLASH_NEWS_ITEMS}}', flash_html)

    # 文章內容區塊
    content_html = build_content_sections(design_articles, gov_articles, summaries)
    template = template.replace('{{CONTENT_SECTIONS}}', content_html)

    return template


def build_content_sections(design_articles, gov_articles, summaries):
    """建立兩個分類的文章列表 HTML"""
    articles_data = summaries.get('articles', [])

    def get_summary(index):
        for a in articles_data:
            if a.get('index') == index:
                return a
        return None

    sections_html = ''

    # 設計區塊
    sections_html += '    <div class="list-block">\n'
    sections_html += '      <div class="section-heading">🎨 設計趨勢、視覺美學與 UI/UX · Design, Aesthetics & UX</div>\n'
    sections_html += '      <div class="item-grid">\n'
    for i, article in enumerate(design_articles):
        idx = i + 1
        summary = get_summary(idx) or {}
        sections_html += build_article_item(article, idx, summary)
    sections_html += '      </div>\n'
    sections_html += '    </div>\n\n'

    # 治理區塊
    sections_html += '    <div class="list-block">\n'
    sections_html += '      <div class="section-heading">🏛️ 公共治理、社會創新與數位政府 · Governance, Civic Innovation & Digital Gov</div>\n'
    sections_html += '      <div class="item-grid">\n'
    for i, article in enumerate(gov_articles):
        idx = len(design_articles) + i + 1
        summary = get_summary(idx) or {}
        sections_html += build_article_item(article, i + 1, summary)
    sections_html += '      </div>\n'
    sections_html += '    </div>\n'

    return sections_html


def build_article_item(article, num, summary):
    """建立單篇文章的 HTML"""
    title = html.escape(article['title'])
    url = html.escape(article['url'])
    source = html.escape(article['source'])
    summary_zh = html.escape(summary.get('summary_zh', article.get('description', '')[:100]))
    summary_en = html.escape(summary.get('summary_en', article['title']))

    # 決定配圖：優先用 og:image，其次用 feed 中的圖
    image_url = article.get('og_image') or article.get('image_from_feed')

    item_html = f'''        <div class="item">
          <div class="item-num">{num:02d}</div>
          <div class="item-body">
            <div class="item-title"><a href="{url}" target="_blank" rel="noopener">{title}</a></div>
'''

    if image_url:
        img_url_escaped = html.escape(image_url)
        item_html += f'            <img class="item-image" src="{img_url_escaped}" alt="{title}" loading="lazy" onerror="this.style.display=\'none\'">\n'

    item_html += f'''            <div class="item-sentence lang-zh-only">{summary_zh} <span class="src">— {source}</span></div>
            <div class="item-sentence-en lang-en-only">{summary_en} <span class="src">— {source}</span></div>
          </div>
        </div>
'''
    return item_html


# ──────────────────────────────────────────────
# 6. Index 歸檔更新模組
# ──────────────────────────────────────────────

def update_index_archive():
    """掃描 briefs/ 目錄，更新 index.html 的歸檔卡片"""
    if not os.path.exists(BRIEFS_DIR):
        os.makedirs(BRIEFS_DIR, exist_ok=True)

    pattern = os.path.join(BRIEFS_DIR, "morning_brief_*.html")
    files = sorted(glob.glob(pattern), reverse=True)

    ref_dir = os.path.join(WORKSPACE_DIR, "參考")
    ref_pattern = os.path.join(ref_dir, "morning_brief_*.html")
    ref_files = glob.glob(ref_pattern) if os.path.exists(ref_dir) else []

    all_cards = []

    for filepath in files:
        filename = os.path.basename(filepath)
        match = re.search(r'morning_brief_(\d{4}-\d{2}-\d{2})\.html', filename)
        if match:
            date_str = match.group(1)
            title = "每日設計與治理簡報"
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read(5000)  # 只讀開頭找標題
                    h_match = re.search(r'<div class="headline">(.*?)</div>', content, re.DOTALL)
                    if h_match:
                        raw_title = re.sub('<[^<]+?>', '', h_match.group(1)).strip()
                        raw_title = re.sub(r'^早安\s*\w+，?', '', raw_title).strip()
                        if raw_title:
                            title = raw_title
            except Exception as e:
                print(f"  ⚠ Error reading {filepath}: {e}")

            all_cards.append({
                'rel_path': f'briefs/{filename}',
                'date_str': date_str,
                'title': title[:55] + ('...' if len(title) > 55 else ''),
                'tags': ['設計美學', '公共治理', 'RSS即時']
            })

    for filepath in ref_files:
        filename = os.path.basename(filepath)
        match = re.search(r'morning_brief_(\d{4}-\d{2}-\d{2})\.html', filename)
        if match:
            date_str = match.group(1)
            all_cards.append({
                'rel_path': f'參考/{filename}',
                'date_str': date_str,
                'title': '參考樣例',
                'tags': ['參考範例']
            })

    all_cards.sort(key=lambda x: x['date_str'], reverse=True)

    cards_html = ""
    for card in all_cards:
        tags_html = "".join([f'<span class="tag">{t}</span>' for t in card['tags']])
        cards_html += f"""
      <a href="{card['rel_path']}" class="brief-card">
        <div>
          <div class="card-date">{card['date_str']}</div>
          <div class="card-title">{card['title']}</div>
        </div>
        <div class="card-tags">
          {tags_html}
        </div>
      </a>"""

    if os.path.exists(INDEX_PATH):
        with open(INDEX_PATH, 'r', encoding='utf-8') as f:
            index_content = f.read()

        replacement = f"<!-- BRIEF_CARDS_START -->{cards_html}\n<!-- BRIEF_CARDS_END -->"
        new_index = re.sub(
            r'<!-- BRIEF_CARDS_START -->.*?<!-- BRIEF_CARDS_END -->',
            replacement,
            index_content,
            flags=re.DOTALL
        )
        with open(INDEX_PATH, 'w', encoding='utf-8') as f:
            f.write(new_index)
        print("✅ Updated index.html archive cards")
    else:
        print("⚠ index.html not found, skipping archive update")


# ──────────────────────────────────────────────
# 7. 審計紀錄模組
# ──────────────────────────────────────────────

def write_audit_log(design_articles, gov_articles, all_raw_articles, date_str):
    """產出 audit JSON，記錄爬取與驗證結果"""
    os.makedirs(AUDIT_DIR, exist_ok=True)
    audit = {
        'date': date_str,
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'total_raw_articles': len(all_raw_articles),
        'total_verified': sum(1 for a in all_raw_articles if a['verified']),
        'total_failed': sum(1 for a in all_raw_articles if not a['verified']),
        'selected_design': len(design_articles),
        'selected_gov': len(gov_articles),
        'articles': [
            {
                'title': a['title'],
                'url': a['url'],
                'source': a['source'],
                'category': a['category'],
                'verified': a['verified'],
                'has_og_image': bool(a.get('og_image')),
                'pub_date': a.get('pub_date'),
            }
            for a in all_raw_articles
        ]
    }
    audit_path = os.path.join(AUDIT_DIR, f'audit_{date_str}.json')
    with open(audit_path, 'w', encoding='utf-8') as f:
        json.dump(audit, f, ensure_ascii=False, indent=2)
    print(f"📋 Audit log written: {audit_path}")


# ──────────────────────────────────────────────
# 8. 主程式
# ──────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="設計與治理日報 · 每日自動生成")
    parser.add_argument('--update-index-only', action='store_true',
                        help="僅更新 index.html 歸檔卡片，不生成新日報")
    parser.add_argument('--date', type=str, default=None,
                        help="指定日期 (YYYY-MM-DD)，預設為今天")
    parser.add_argument('--skip-gemini', action='store_true',
                        help="跳過 Gemini 摘要，使用文章自帶描述")
    args = parser.parse_args()

    if args.update_index_only:
        update_index_archive()
        return

    # 決定日期
    tw_tz = timezone(timedelta(hours=8))
    if args.date:
        date_str = args.date
    else:
        date_str = datetime.now(tw_tz).strftime('%Y-%m-%d')

    print(f"\n{'='*60}")
    print(f"  設計與治理日報 · {date_str}")
    print(f"{'='*60}\n")

    # Step 1: 爬取所有 RSS feeds
    print("=" * 40)
    print("STEP 1: 爬取 RSS Feeds")
    print("=" * 40)
    all_articles = []
    for feed in RSS_FEEDS:
        articles = parse_rss_feed(feed['url'], feed['source_name'], feed['category'])
        all_articles.extend(articles)

    if not all_articles:
        print("❌ 未能從任何 RSS 來源爬取到文章，程序終止")
        sys.exit(1)

    print(f"\n📊 Total raw articles from RSS: {len(all_articles)}")

    # Step 2: HTTP 驗證 + og:image 擷取
    print("\n" + "=" * 40)
    print("STEP 2: HTTP 驗證 + og:image 擷取")
    print("=" * 40)
    for article in all_articles:
        verify_and_enrich_article(article)

    verified_count = sum(1 for a in all_articles if a['verified'])
    print(f"\n📊 Verified: {verified_count}/{len(all_articles)}")

    # Step 3: 選出最終文章
    print("\n" + "=" * 40)
    print("STEP 3: 篩選最終文章")
    print("=" * 40)
    design_articles, gov_articles = select_articles(all_articles)

    if len(design_articles) == 0 and len(gov_articles) == 0:
        print("❌ 篩選後無可用文章，程序終止")
        sys.exit(1)

    # Step 4: LLM 摘要
    print("\n" + "=" * 40)
    print("STEP 4: 產出摘要")
    print("=" * 40)
    if args.skip_gemini:
        summaries = generate_fallback_summaries(design_articles, gov_articles, date_str)
    else:
        summaries = generate_summaries_with_gemini(design_articles, gov_articles, date_str)

    # Step 5: 生成 HTML
    print("\n" + "=" * 40)
    print("STEP 5: 生成 HTML")
    print("=" * 40)
    brief_html = generate_brief_html(design_articles, gov_articles, summaries, date_str)
    os.makedirs(BRIEFS_DIR, exist_ok=True)
    brief_path = os.path.join(BRIEFS_DIR, f'morning_brief_{date_str}.html')
    with open(brief_path, 'w', encoding='utf-8') as f:
        f.write(brief_html)
    print(f"✅ Brief generated: {brief_path}")

    # Step 6: 更新 index.html
    print("\n" + "=" * 40)
    print("STEP 6: 更新 index.html")
    print("=" * 40)
    update_index_archive()

    # Step 7: 審計紀錄
    print("\n" + "=" * 40)
    print("STEP 7: 審計紀錄")
    print("=" * 40)
    write_audit_log(design_articles, gov_articles, all_articles, date_str)

    # 最終摘要
    print(f"\n{'='*60}")
    print(f"  ✅ 日報生成完成！")
    print(f"  📄 {brief_path}")
    print(f"  📊 設計 {len(design_articles)} 篇 + 治理 {len(gov_articles)} 篇")
    print(f"  🖼️  含 og:image {sum(1 for a in design_articles + gov_articles if a.get('og_image'))} 篇")
    print(f"{'='*60}\n")


if __name__ == '__main__':
    main()
