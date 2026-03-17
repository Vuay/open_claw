import sqlite3
import re
from datetime import datetime
from collections import Counter

class Meditation:
    def __init__(self, db_path):
        self.db_path = db_path
    
    def get_recent_conversations(self, hours=18):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute("""
            SELECT id, title, message, time 
            FROM conversation 
            WHERE message IS NOT NULL 
            AND message NOT LIKE '%cron%'
            AND LENGTH(message) > 50
            ORDER BY time DESC
            LIMIT 50
        """)
        results = cursor.fetchall()
        conn.close()
        return results
    
    def extract_insights(self, conversations):
        insights = {'key_concepts': [], 'common_questions': [], 'solutions': []}
        
        all_text = " ".join([c[2] or "" for c in conversations])
        
        # 关键词
        words = re.findall(r'\w{4,}', all_text.lower())
        insights['key_concepts'] = [w for w, c in Counter(words).most_common(15)]
        
        # 问题
        questions = re.findall(r'[^。.]*\?[^。.]*', all_text)
        insights['common_questions'] = list(set(questions[:8]))
        
        # 解决方案
        solutions = re.findall(r'[^。.]*(?:解决|修复|方案|完成|成功|部署|安装)[^。.]*', all_text)
        insights['solutions'] = list(set(solutions[:8]))
        
        return insights
    
    def generate_prompts(self, insights):
        prompts = []
        if insights['key_concepts']:
            prompts.append(f"### 关键概念\n{', '.join(insights['key_concepts'])}")
        if insights['solutions']:
            prompts.append(f"### 最佳实践\n" + "\n".join([f"- {s}" for s in insights['solutions']]))
        return "\n\n".join(prompts)
    
    def meditate(self, hours=18):
        conversations = self.get_recent_conversations(hours)
        if not conversations:
            return {'status': 'no_data', 'message': '没有足够的数据进行冥想'}
        
        insights = self.extract_insights(conversations)
        prompts = self.generate_prompts(insights)
        
        return {
            'time': datetime.now().isoformat(),
            'conversations_count': len(conversations),
            'insights': insights,
            'prompts': prompts
        }
    
    def save_meditation(self, result):
        import json
        from pathlib import Path
        d = Path('/root/.openclaw/knowledge/meditation')
        d.mkdir(exist_ok=True)
        f = d / f'meditation_{datetime.now().strftime("%Y-%m-%d")}.json'
        with open(f, 'w', encoding='utf-8') as file:
            json.dump(result, file, ensure_ascii=False, indent=2)
        return str(f)

meditation = Meditation('/root/.openclaw/memory_system/data/memory.db')
