#!/usr/bin/env python3
import os
import re
import glob

WORKSPACE_DIR = os.path.dirname(os.path.abspath(__file__))
BRIEFS_DIR = os.path.join(WORKSPACE_DIR, 'briefs')
INDEX_PATH = os.path.join(WORKSPACE_DIR, 'index.html')

def update_index_archive():
    """自動掃描 briefs/ 目錄下的所有 HTML 簡報，並更新 index.html 歸檔頁面"""
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
                'tags': ['UI/UX', 'AI治理', '政府創新']
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

if __name__ == '__main__':
    update_index_archive()
