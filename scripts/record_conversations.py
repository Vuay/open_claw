#!/usr/bin/env python3
"""
自动对话记录器 - 从OpenClaw会话中提取对话并保存
- 记录所有会话的对话内容
- 生成摘要
- 保存到记忆系统
"""
import os
import json
import uuid
from datetime import datetime
from pathlib import Path

WORKSPACE = "/root/.openclaw/workspace"
SESSIONS_DIR = "/root/.openclaw/agents/main/sessions"
CONVERSATIONS_FILE = os.path.join(WORKSPACE, "memory/conversations.json")
VECTORS_FILE = os.path.join(WORKSPACE, "memory/vectors.json")

def load_sessions():
    """加载所有会话"""
    sessions_file = os.path.join(SESSIONS_DIR, "sessions.json")
    if not os.path.exists(sessions_file):
        return {}
    
    with open(sessions_file, 'r') as f:
        return json.load(f)

def read_session_messages(session_file):
    """读取会话消息"""
    if not os.path.exists(session_file):
        return []
    
    messages = []
    with open(session_file, 'r') as f:
        for line in f:
            try:
                data = json.loads(line.strip())
                if data.get('type') == 'message':
                    msg = data.get('message', {})
                    role = msg.get('role', '')
                    content_parts = msg.get('content', [])
                    
                    # 提取文本内容
                    text = ''
                    if isinstance(content_parts, list):
                        for part in content_parts:
                            if isinstance(part, dict):
                                if part.get('type') == 'text':
                                    text += part.get('text', '')
                                elif part.get('type') == 'toolUse':
                                    # 工具调用
                                    text += f"\n[工具: {part.get('name', 'unknown')}] "
                                    inp = part.get('input', {})
                                    if isinstance(inp, dict):
                                        text += json.dumps(inp, ensure_ascii=False)[:200]
                                elif part.get('type') == 'toolResult':
                                    text += f"\n[结果] {part.get('content', '')[:200]}"
                    
                    if text and role in ['user', 'assistant']:
                        messages.append({
                            'role': role,
                            'content': text.strip()[:500],  # 限制长度
                            'timestamp': data.get('timestamp', '')
                        })
            except:
                continue
    
    return messages

def generate_summary(messages):
    """生成对话摘要"""
    if not messages:
        return "", ""
    
    # 获取第一条用户消息作为标题
    title = ""
    for msg in messages:
        if msg['role'] == 'user':
            content = msg['content'][:100]
            title = content.replace('\n', ' ')
            break
    
    # 合并所有消息作为摘要
    summary_parts = []
    for msg in messages[:10]:  # 取前10条
        role_emoji = "👤" if msg['role'] == 'user' else "🤖"
        content = msg['content'][:200].replace('\n', ' ')
        summary_parts.append(f"{role_emoji} {content}")
    
    summary = "\n".join(summary_parts)
    if len(messages) > 10:
        summary += f"\n\n... 共 {len(messages)} 条消息"
    
    return title, summary

def load_existing_conversations():
    """加载已保存的对话"""
    if not os.path.exists(CONVERSATIONS_FILE):
        return []
    
    try:
        with open(CONVERSATIONS_FILE, 'r') as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            elif isinstance(data, dict):
                return data.get('conversations', [])
    except:
        return []
    
    return []

def save_conversations(conversations):
    """保存对话到文件"""
    with open(CONVERSATIONS_FILE, 'w', encoding='utf-8') as f:
        json.dump({
            'conversations': conversations,
            'last_updated': datetime.now().isoformat()
        }, f, ensure_ascii=False, indent=2)

def record_conversations():
    """主函数：记录所有对话"""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 开始记录对话...")
    
    # 加载已有记录
    existing = load_existing_conversations()
    existing_ids = set(c.get('id', '') for c in existing)
    
    # 加载会话列表
    sessions = load_sessions()
    print(f"发现 {len(sessions)} 个会话")
    
    new_count = 0
    for session_key, session_info in sessions.items():
        session_file = session_info.get('sessionFile')
        if not session_file or not os.path.exists(session_file):
            continue
        
        # 跳过reset文件
        if '.reset.' in session_file:
            continue
        
        # 生成会话ID
        session_id = os.path.basename(session_file).replace('.jsonl', '')
        
        # 跳过已记录的
        if session_id in existing_ids:
            continue
        
        # 读取消息
        messages = read_session_messages(session_file)
        if not messages:
            continue
        
        # 生成摘要
        title, summary = generate_summary(messages)
        if not summary:
            continue
        
        # 创建记录
        conv = {
            'id': session_id,
            'time': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'title': title or f'对话 {session_id[:8]}',
            'summary': summary[:1000],
            'messages_count': len(messages)
        }
        
        existing.append(conv)
        new_count += 1
        print(f"✓ 记录: {conv['title'][:50]}")
    
    # 保存
    if new_count > 0:
        save_conversations(existing)
        print(f"完成! 新增 {new_count} 条对话记录，共 {len(existing)} 条")
    else:
        print("没有新对话需要记录")
    
    return new_count

if __name__ == '__main__':
    record_conversations()
