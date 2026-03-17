#!/usr/bin/env python3
"""增强版会话同步 - 从jsonl文件提取完整对话"""
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
                if not line.strip():
                    continue
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
                except:
                    continue
    except:
        pass
    return messages

def save_conversation(session_id, messages, conn):
    if not messages:
        return 0
    
    full_text = ""
    for m in messages:
        role_emoji = "👤" if m['role'] == 'user' else "🤖"
        full_text += f"{role_emoji} {m['role']}: {m['content']}\n\n"
    
    title = messages[0]['content'][:80] if messages else "对话"
    
    c = conn.cursor()
    c.execute("SELECT id FROM conversation WHERE id = ?", (session_id,))
    exists = c.fetchone()
    
    if not exists:
        c.execute("""INSERT INTO conversation (id, title, summary, message, time, messages_count, tags)
            VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (session_id, title, f"{len(messages)}条消息", full_text,
             datetime.now().strftime('%Y-%m-%d %H:%M'), len(messages), "dialogue"))
        conn.commit()
        return 1
    return 0

def sync_sessions():
    conn = sqlite3.connect(DB_PATH)
    saved = 0
    
    c = conn.cursor()
    c.execute("DELETE FROM conversation WHERE message LIKE '%cron:%' OR message IS NULL")
    conn.commit()
    
    sessions_path = Path(SESSIONS_DIR)
    if sessions_path.exists():
        for session_file in sessions_path.glob("*.jsonl"):
            if '.deleted.' in session_file.name:
                continue
            session_id = session_file.stem
            messages = extract_conversation(session_file)
            if messages:
                saved += save_conversation(session_id, messages, conn)
    
    conn.close()
    print(f"同步完成: {saved} 条新对话")
    return saved

if __name__ == '__main__':
    sync_sessions()
