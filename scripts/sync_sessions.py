#!/usr/bin/env python3
"""增强版会话同步 - 完整问答格式"""
import os, json, sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = "/root/.openclaw/memory_system/data/memory.db"
SESSIONS_DIR = "/root/.openclaw/agents/main/sessions"

def extract_conversation(filepath):
    messages = []
    try:
        with open(filepath, 'r') as f:
            for line in f:
                if not line.strip(): continue
                try:
                    data = json.loads(line)
                    if data.get('type') == 'message':
                        msg = data.get('message', {})
                        role = msg.get('role', '')
                        content = msg.get('content', [])
                        
                        text_content = []
                        for c in content:
                            if isinstance(c, dict):
                                if c.get('type') == 'text':
                                    text_content.append(c.get('text', ''))
                                elif c.get('type') == 'thinking':
                                    text_content.append('[思考] ' + c.get('thinking', ''))
                        
                        full_text = '\n'.join(text_content)
                        if full_text and role in ['user', 'assistant']:
                            messages.append({'role': role, 'content': full_text[:2000]})
                except: continue
    except: pass
    return messages

def save_full_conversation(session_id, messages):
    if not messages: return 0
    
    qa_pairs = []
    for msg in messages:
        role = msg.get('role', '')
        content = msg.get('content', '')
        
        if role == 'user':
            qa_pairs.append({'question': content, 'answer': ''})
        elif role == 'assistant':
            if qa_pairs and not qa_pairs[-1]['answer']:
                qa_pairs[-1]['answer'] = content
    
    if not qa_pairs: return 0
    
    readable = ""
    for i, qa in enumerate(qa_pairs, 1):
        readable += f"❓ 问题{i}: {qa['question']}\n"
        readable += f"✅ 回答{i}: {qa['answer']}\n"
        readable += "---\n"
    
    title = qa_pairs[0]['question'][:50]
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute("""
        INSERT OR REPLACE INTO conversation 
        (id, title, summary, message, time, messages_count, tags)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (session_id, title, f"{len(qa_pairs)}个问答", readable,
          datetime.now().isoformat(), len(messages), 'dialogue'))
    
    conn.commit()
    conn.close()
    return len(qa_pairs)

def sync_sessions():
    saved = 0
    sessions_path = Path(SESSIONS_DIR)
    if sessions_path.exists():
        for session_file in sessions_path.glob("*.jsonl"):
            if '.deleted.' in session_file.name: continue
            session_id = session_file.stem
            messages = extract_conversation(session_file)
            if messages:
                saved += save_full_conversation(session_id, messages)
    print(f"同步完成: {saved} 条问答")
    return saved

if __name__ == '__main__':
    sync_sessions()
