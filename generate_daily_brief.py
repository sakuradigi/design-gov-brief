#!/usr/bin/env python3
import os
import re
import glob
import json
import urllib.request
import xml.etree.ElementTree as ET
from urllib.parse import urlparse
import argparse
from datetime import datetime

WORKSPACE_DIR = os.path.dirname(os.path.abspath(__file__))
BRIEFS_DIR = os.path.join(WORKSPACE_DIR, 'briefs')
INDEX_PATH = os.path.join(WORKSPACE_DIR, 'index.html')
TEMPLATE_PATH = os.path.join(WORKSPACE_DIR, 'templates', 'brief_template.html')

# 高畫質真實設計與藝術圖床備用庫 (Unsplash Design & Motion HD Collections)
DESIGN_AESTHETIC_IMAGES = [
    ("https://images.unsplash.com/photo-1561070791-2526d30994b5?auto=format&fit=crop&w=1200&q=80", "平面設計與字體美學風格展示"),
    ("https://images.unsplash.com/photo-1550745165-9bc0b252726f?auto=format&fit=crop&w=1200&q=80", "動態視覺與空間光影藝術展示"),
    ("https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&w=1200&q=80", "抽象幾何與現代視覺美學展示"),
    ("https://images.unsplash.com/photo-1507238691740-187a5b1d37b8?auto=format&fit=crop&w=1200&q=80", "數位 UI/UX 介面美學與系統展示")
]

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'}

def scrape_realtime_rss_news():
    """先抓後寫鐵律：發起實體 RSS 爬蟲，獲取當前 2026 最新發布的新聞與文章標題/網址"""
    rss_design = 'https://news.google.com/rss/search?q=graphic+design+OR+motion+design+OR+UX+design+when:7d&hl=en-US&gl=US&ceid=US:en'
    rss_gov = 'https://news.google.com/rss/search?q=digital+governance+OR+civic+tech+OR+public+sector+AI+when:7d&hl=en-US&gl=US&ceid=US:en'

    def fetch_items(rss_url, count=5):
        try:
            req = urllib.request.Request(rss_url, headers=headers)
            with urllib.request.urlopen(req, timeout=6) as resp:
                root = ET.fromstring(resp.read())
            items = []
            for item in root.findall('.//item'):
                title = item.find('title').text if item.find('title') is not None else ''
                link = item.find('link').text if item.find('link') is not None else ''
                pub_date = item.find('pubDate').text if item.find('pubDate') is not None else ''
                if title and link:
                    # 去除標題尾端的媒體名稱洗牌
                    clean_title = re.sub(r'\s*-\s*[^-]+$', '', title).strip()
                    items.append({'title': clean_title, 'url': link, 'pub_date': pub_date})
                    if len(items) >= count:
                        break
            return items
        except Exception as e:
            print(f"RSS Scrape Notice: {e}")
            return []

    design_items = fetch_items(rss_design, 5)
    gov_items = fetch_items(rss_gov, 5)
    return design_items, gov_items

def fetch_og_image(url):
    """雲端實時抓取文章的 Open Graph 預覽配圖 (og:image)"""
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=5) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
            m = re.search(r'<meta[^>]+property=[\"\']og:image[\"\'][^>]+content=[\"\']([^\"\']+)[\"\']', html, re.I)
            if not m:
                m = re.search(r'<meta[^>]+content=[\"\']([^\"\']+)[\"\'][^>]+property=[\"\']og:image[\"\']', html, re.I)
            if m:
                img_url = m.group(1).strip()
                if img_url.startswith('/'):
                    parsed = urlparse(url)
                    img_url = f"{parsed.scheme}://{parsed.netloc}{img_url}"
                return img_url
    except Exception as e:
        print(f"OG Image Fetch Notice for {url}: {e}")
    return None

def generate_news_with_gemini(api_key, date_str):
    """先抓後寫鐵律：將實體爬取的 2026 新聞標題與網址餵給 Gemini 進行白話洞見提煉"""
    scraped_design, scraped_gov = scrape_realtime_rss_news()

    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        
        model = genai.GenerativeModel('gemini-3.6-flash')
        
        prompt = f"""你是一個懂設計、懂治理又超會聊天的「視覺美學與社會創新日報」總編輯。
今天是 {date_str}。以下是剛剛發起實體爬蟲抓到的 2026 最新真實新聞標題與網址：

【實體爬取之設計與美學新聞】：
{json.dumps(scraped_design, ensure_ascii=False, indent=2)}

【實體爬取之公共治理新聞】：
{json.dumps(scraped_gov, ensure_ascii=False, indent=2)}

【白話洞見與 100% 文章匹配硬性規範】：
1. 100% 真實對應：你撰寫的每一則摘要與標題，必須 100% 來自上方傳入的真實新聞標題與網址！絕對禁止自創網址、絕對禁止張冠李戴！
2. 白話通俗口吻：絕對不要寫成生硬的學術論文或公文！請用「白話、通俗、精闢、極好閱讀」的對話口吻，開門見山講這件事為什麼跟你有關。
3. 當日獨特標題 (Headline)：`headline` 必須依據今日實體新聞最吸睛的核心內容，寫出獨特且有吸引力的大標題（如「歐元紙幣美學競賽、公共 AI 整備度警訊與東非數據治理」），絕對禁止使用固定套版！

請依據以下格式輸出純 JSON (不要包含 markdown 標籤)：
{{
  "headline": "根據今日實體新聞提煉的動態大標題 (25字內，展示今日獨特關鍵字)",
  "quote_en": "英文名人格言",
  "quote_zh": "繁體中文格言翻譯",
  "quote_author": "作者名字",
  "flash_takeaways": [
    "<span class=\\\"flash-tag\\\">美學趨勢</span> 通俗白話一句話洞見 1",
    "<span class=\\\"flash-tag\\\">公共治理</span> 通俗白話一句話洞見 2",
    "<span class=\\\"flash-tag\\\">科技分寸</span> 通俗白話一句話洞見 3"
  ],
  "design_news": [
    {{
      "title": "上方傳入之真實設計新聞標題 1",
      "url": "上方傳入之真實設計新聞網址 1",
      "sentence_zh": "<span class=\\\"aesthetic-tag\\\">視覺美學</span> 白話通俗洞見...",
      "sentence_en": "<span class=\\\"aesthetic-tag\\\">Graphic Aesthetics</span> Plain English insight..."
    }}
  ],
  "gov_news": [
    {{
      "title": "上方傳入之真實治理新聞標題 1",
      "url": "上方傳入之真實治理新聞網址 1",
      "sentence_zh": "<span class=\\\"civic-tag\\\">治理創新</span> 白話通俗洞見...",
      "sentence_en": "<span class=\\\"civic-tag\\\">Civic Experiment</span> Plain English insight..."
    }}
  ]
}}
"""
        response = model.generate_content(prompt)
        text = response.text.strip()
        text = re.sub(r'^```json\s*', '', text)
        text = re.sub(r'\s*```$', '', text)
        data = json.loads(text)
        return data
    except Exception as e:
        print(f"Gemini API generation failed/fallback: {e}")
        return None

def build_html_from_data(data, date_str):
    """將實體抓取與 Gemini 摘要填入模板，並輸出至 briefs/"""
    if not os.path.exists(TEMPLATE_PATH):
        print(f"Template not found at {TEMPLATE_PATH}")
        return False

    with open(TEMPLATE_PATH, 'r', encoding='utf-8') as f:
        tmpl = f.read()

    # 快訊列表 (極簡精準 3 句)
    flash_html = ""
    for item in data.get('flash_takeaways', []):
        flash_html += f"""
        <li class="flash-item">
          {item}
        </li>"""

    # 設計新聞 5 則
    design_items_html = ""
    for i, item in enumerate(data.get('design_news', []), 1):
        url = item.get('url', '#')
        title = item.get('title', '')
        zh = item.get('sentence_zh', '')
        en = item.get('sentence_en', '')
        
        og_img = fetch_og_image(url) if url != '#' else None
        img_html = ""
        if og_img:
            img_html = f"""
            <img class="item-image" src="{og_img}" alt="{title}">
            <div class="item-image-caption">🖼️ 專文實體配圖：擷取自 {urlparse(url).netloc} 文章原文</div>"""
        elif i <= len(DESIGN_AESTHETIC_IMAGES):
            fallback_img, caption = DESIGN_AESTHETIC_IMAGES[i-1]
            img_html = f"""
            <img class="item-image" src="{fallback_img}" alt="{title}">
            <div class="item-image-caption">🖼️ 美學選圖：{caption}</div>"""

        design_items_html += f"""
        <div class="item">
          <div class="item-num">{i}</div>
          <div class="item-body">
            <div class="item-title"><a href="{url}" target="_blank" rel="noopener">{title}</a></div>
            {img_html}
            <div class="item-sentence lang-zh-only">{zh} <a class="src" href="{url}" target="_blank" rel="noopener">來源專文</a></div>
            <div class="item-sentence-en lang-en-only">{en} <a class="src" href="{url}" target="_blank" rel="noopener">Source Article</a></div>
          </div>
        </div>"""

    # 治理新聞 5 則
    gov_items_html = ""
    for i, item in enumerate(data.get('gov_news', []), 1):
        url = item.get('url', '#')
        title = item.get('title', '')
        zh = item.get('sentence_zh', '')
        en = item.get('sentence_en', '')
        
        og_img = fetch_og_image(url) if url != '#' else None
        img_html = ""
        if og_img:
            img_html = f"""
            <img class="item-image" src="{og_img}" alt="{title}">
            <div class="item-image-caption">🖼️ 報告實體配圖：擷取自 {urlparse(url).netloc} 官方門戶</div>"""

        gov_items_html += f"""
        <div class="item">
          <div class="item-num">{i}</div>
          <div class="item-body">
            <div class="item-title"><a href="{url}" target="_blank" rel="noopener">{title}</a></div>
            {img_html}
            <div class="item-sentence lang-zh-only">{zh} <a class="src" href="{url}" target="_blank" rel="noopener">來源專文</a></div>
            <div class="item-sentence-en lang-en-only">{en} <a class="src" href="{url}" target="_blank" rel="noopener">Source Article</a></div>
          </div>
        </div>"""

    sections_html = f"""
    <div class="list-block" style="margin-top: 36px;">
      <div class="section-heading">🎨 視覺藝術、平面設計趨勢與 UI/UX 美學 · Design Aesthetics & Visual Art (5 則 2026 當前時事)</div>
      <div class="item-grid">{design_items_html}</div>
    </div>
    <div class="list-block">
      <div class="section-heading">🏛️ 全球公共治理、政治性實驗與社會創新 · Public Governance & Civic Innovation (5 則 2026 當前時事)</div>
      <div class="item-grid">{gov_items_html}</div>
    </div>"""

    now_ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S (Asia/Taipei)')

    # 使用當天動態大標題
    headline_text = data.get('headline', f'今日重點：歐元紙幣美學競賽、公共 AI 整備度警訊與東非數據治理 ({date_str})')

    html = tmpl.replace('{{DATE_STRING}}', date_str)
    html = html.replace('{{HEADLINE}}', headline_text)
    html = html.replace('{{QUOTE_EN}}', data.get('quote_en', ''))
    html = html.replace('{{QUOTE_ZH}}', data.get('quote_zh', ''))
    html = html.replace('{{QUOTE_AUTHOR}}', data.get('quote_author', ''))
    html = html.replace('{{FLASH_NEWS_ITEMS}}', flash_html)
    html = html.replace('{{CALM_LINE}}', '為您提煉今日 10 則結合「視覺美學素養、動態藝術、多元治理與科技分寸」的白話洞見：')
    html = html.replace('{{CONTENT_SECTIONS}}', sections_html)
    html = html.replace('{{GENERATED_MODEL}}', 'Gemini 3.6 Flash / Antigravity Agent')
    html = html.replace('{{GENERATION_TIMESTAMP}}', now_ts)

    output_filename = f"morning_brief_{date_str}.html"
    output_path = os.path.join(BRIEFS_DIR, output_filename)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"Successfully generated HTML brief with real scraped news at: {output_path}")
    return True

def update_index_archive():
    """自動掃描 briefs/ 與 參考/ 目錄下的所有 HTML 簡報，並動態抓取當天獨立的大標題作為歸檔卡片標題"""
    if not os.path.exists(BRIEFS_DIR):
        os.makedirs(BRIEFS_DIR, exist_ok=True)

    pattern = os.path.join(BRIEFS_DIR, "morning_brief_*.html")
    files = sorted(glob.glob(pattern), reverse=True)
    
    ref_pattern = os.path.join(WORKSPACE_DIR, "參考", "morning_brief_*.html")
    ref_files = glob.glob(ref_pattern)
    
    all_cards = []
    
    for filepath in files:
        filename = os.path.basename(filepath)
        match = re.search(r'morning_brief_(\d{4}-\d{2}-\d{2})\.html', filename)
        if match:
            date_str = match.group(1)
            title = "每日設計與 AI 治理簡報"
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    h_match = re.search(r'<div class="headline">(.*?)</div>', content, re.DOTALL)
                    if h_match:
                        raw_title = re.sub('<[^<]+?>', '', h_match.group(1)).strip()
                        title = re.sub(r'^早安\s*\w+，?', '', raw_title).strip()
            except Exception as e:
                print(f"Error reading {filepath}: {e}")

            all_cards.append({
                'rel_path': f'briefs/{filename}',
                'date_str': date_str,
                'title': title[:55] + ('...' if len(title) > 55 else ''),
                'tags': ['美學設計', '多元治理', '2026時事']
            })

    for filepath in ref_files:
        filename = os.path.basename(filepath)
        match = re.search(r'morning_brief_(\d{4}-\d{2}-\d{2})\.html', filename)
        if match:
            date_str = match.group(1)
            all_cards.append({
                'rel_path': f'參考/{filename}',
                'date_str': date_str,
                'title': "HCI研討會與 DESIGN.md 生成規範 (參考樣例)",
                'tags': ['UI/UX', 'AI規範', '參考範例']
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
        print("Updated index.html successfully with dynamic daily titles.")

def main():
    parser = argparse.ArgumentParser(description="Generate Daily Brief & Update Index")
    parser.add_argument('--update-index-only', action='store_true', help="Only update index.html archive list")
    args = parser.parse_args()

    api_key = os.environ.get('GEMINI_API_KEY')
    date_str = datetime.now().strftime('%Y-%m-%d')
    
    if api_key and not args.update_index_only:
        print("Running in Cloud mode with GEMINI_API_KEY...")
        data = generate_news_with_gemini(api_key, date_str)
        if data:
            print("Successfully generated daily data via Gemini 3.6 Flash API under Scrape-First real-time news architecture.")
            build_html_from_data(data, date_str)
    
    update_index_archive()

if __name__ == '__main__':
    main()
