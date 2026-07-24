#!/usr/bin/env python3
import os
import re
import glob
import json
import urllib.request
import argparse
from datetime import datetime

WORKSPACE_DIR = os.path.dirname(os.path.abspath(__file__))
BRIEFS_DIR = os.path.join(WORKSPACE_DIR, 'briefs')
INDEX_PATH = os.path.join(WORKSPACE_DIR, 'index.html')

def verify_url_live(url):
    """在沙盒/雲端環境中發送 HTTP GET 請求驗證 URL 是否回傳 HTTP 200 OK 避免 404 死連結"""
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'})
        with urllib.request.urlopen(req, timeout=6) as resp:
            return resp.status == 200
    except Exception as e:
        print(f"URL Verification Failed for {url}: {e}")
        return False

def generate_news_with_gemini(api_key, date_str):
    """在 GitHub Actions 雲端環境中使用 Gemini API 檢索最新主題新聞（嚴格遵循 10 獨立網域、AI佔比控管、美學選圖與政治性實驗規範）"""
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        
        model = genai.GenerativeModel('gemini-3.6-flash')
        
        prompt = f"""你是一個專業的「視覺美學、平面動態與多元公共治理日報」總編輯。
今天是 {date_str}。請協助檢索並撰寫今日全球最優質的主題新知。

【雲端生成硬性規範】：
1. 比例控管：每日兩大領域中，AI 相關議題「各佔 2 ~ 3 則為上限」，絕對不畫地自限只寫 AI！
2. 🎨 設計與美學板塊 (5 則)：
   - 2~3 則涵蓋平面設計趨勢 (Graphic Design)、動態視覺 (Motion Design)、視覺藝術與色彩字體美學。
   - 2 則涵蓋 AI 原生 UI/UX 人機協作與設計系統。
3. 🏛️ 公共治理與社會創新板塊 (5 則)：
   - 2~3 則涵蓋政治性實驗 (Civic Experiments)、參與式審議民主沙盒、新型治理思維、數位公共基礎設施 (DPI) 與白話公共服務。
   - 2 則涵蓋 AI 治理與公共問責。
4. 網域多樣性：10 則新聞必須來自 10 個完全不同的權威機構與網域 (Domains)。
5. 連結真實性：所有網址必須為實時可點開的完整專文或報告 URL，禁止拼湊無效 404 連結！
6. 洞見品質：摘要必須通俗白話、富有深層戰略洞見，標註「核心洞見」、「平面與視覺美學」或「政治性實驗」。

請依據以下格式輸出純 JSON (不要包含 markdown 標籤)：
{{
  "headline": "晨間問候與今日美學治理主軸 (20字內)",
  "quote_en": "英文名人格言",
  "quote_zh": "繁體中文格言翻譯",
  "quote_author": "作者名字",
  "flash_takeaways": [
    "【視覺與美學】一句話快訊 1",
    "【治理與創新】一句話快訊 2",
    "【科技分寸】一句話快訊 3"
  ],
  "design_news": [
    {{
      "title": "文章標題 1",
      "url": "https://www.nngroup.com/articles/xxx/",
      "sentence_zh": "<span class=\\\"aesthetic-tag\\\">平面與視覺美學</span> 通俗白話洞見...",
      "sentence_en": "<span class=\\\"aesthetic-tag\\\">Graphic Aesthetics</span> English insight..."
    }}
  ],
  "gov_news": [
    {{
      "title": "文章標題 1",
      "url": "https://digital-strategy.ec.europa.eu/en/policies/xxx",
      "sentence_zh": "<span class=\\\"civic-tag\\\">政治性實驗</span> 通俗白話洞見...",
      "sentence_en": "<span class=\\\"civic-tag\\\">Civic Experiment</span> English insight..."
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

def update_index_archive():
    """自動掃描 briefs/ 與 參考/ 目錄下的所有 HTML 簡報，並更新 index.html 歸檔頁面"""
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
                        title = re.sub('<[^<]+?>', '', h_match.group(1)).strip()
            except Exception as e:
                print(f"Error reading {filepath}: {e}")

            all_cards.append({
                'rel_path': f'briefs/{filename}',
                'date_str': date_str,
                'title': title[:50] + ('...' if len(title) > 50 else ''),
                'tags': ['美學設計', '多元治理', '社會創新']
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
        print("Updated index.html successfully.")

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
            print("Successfully generated daily data via Gemini 3.6 Flash API under new aesthetics & civic governance rules.")
    
    update_index_archive()

if __name__ == '__main__':
    main()
