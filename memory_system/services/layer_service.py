#!/usr/bin/env python3
"""
轻量记忆分层服务
- short_term: 24小时内
- long_term: 7天内 (重要对话)
- permanent: 永久 (核心文件)
"""
import os
import sqlite3
from datetime import datetime, timedelta

DB_PATH = "/root/.openclaw/memory_system/data/memory.db"

# 重要关键词
IMPORTANT_KEYWORDS = ['配置', '部署', '修复', '优化', '方案', '记住', 'memory', 'system', 'backup']
CORE_FILES = ['MEMORY.md', 'AGENTS.md', 'SOUL.md', 'TOOLS.md', 'USER.md', 'IDENTITY.md']

def classify_layer(content: str, filename: str = "") -> str:
    """基于规则自动分类"""
    
    # 核心文件 -> permanent
    for f in CORE_FILES:
        if f in filename:
            return 'permanent'
    
    # 重要关键词 -> long_term
    for kw in IMPORTANT_KEYWORDS:
        if kw.lower() in content.lower():
            return 'long_term'
    
    # 默认短期
    return 'short_term'

def get_layer_age(layer: str) -> int:
    """获取层级最大保留时间(小时)"""
    return {'short_term': 24, 'long_term': 168, 'permanent': 0}.get(layer, 24)

def sync_layers():
    """同步记忆分层"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 创建分层表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS memory_layers (
            id INTEGER PRIMARY KEY,
            conversation_id TEXT,
            layer TEXT DEFAULT 'short_term',
            priority INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 获取所有对话
    cursor.execute("SELECT id, message, title FROM conversation")
    conversation = cursor.fetchall()
    
    now = datetime.now()
    
    for conv_id, message, title in conversation:
        # 检查是否已存在
        cursor.execute("SELECT id FROM memory_layers WHERE conversation_id = ?", (conv_id,))
        exists = cursor.fetchone()
        
        if not exists:
            content = (message or '') + (title or '')
            layer = classify_layer(content)
            priority = 1 if layer == 'long_term' else 0
            
            cursor.execute(
                "INSERT INTO memory_layers (conversation_id, layer, priority) VALUES (?, ?, ?)",
                (conv_id, layer, priority)
            )
    
    # 清理过期短期记忆
    cursor.execute(
        "DELETE FROM memory_layers WHERE layer = 'short_term' AND created_at < ?",
        (now - timedelta(hours=24),)
    )
    
    conn.commit()
    conn.close()
    print(f"记忆分层同步完成")

if __name__ == '__main__':
    sync_layers()
