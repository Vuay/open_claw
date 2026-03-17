#!/usr/bin/env python3
"""
实时记忆系统 - 自动记录对话和操作
"""

import os
import json
from pathlib import Path
from datetime import datetime

MEMORY_DIR = Path("/root/.openclaw/workspace/memory")
MEMORY_FILE = MEMORY_DIR / "2026-03-16.md"

def init_memory():
    """初始化记忆文件"""
    if not MEMORY_FILE.exists():
        MEMORY_FILE.write_text(f"""# 记忆仓库 - {datetime.now().strftime('%Y-%m-%d')}

## 对话记录

## 操作记录

---
*实时更新*
""")

def add_record(record_type, content):
    """添加记录"""
    init_memory()
    
    timestamp = datetime.now().strftime("%H:%M")
    
    with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
        content_md = f.read()
    
    if record_type == "对话":
        section = "## 对话记录"
    else:
        section = "## 操作记录"
    
    if section in content_md:
        lines = content_md.split('\n')
        new_lines = []
        found = False
        for line in lines:
            new_lines.append(line)
            if line.strip() == section and not found:
                new_lines.append(f"- **{timestamp}** {content}")
                found = True
        
        if not found:
            new_lines.append(f"\n{section}")
            new_lines.append(f"- **{timestamp}** {content}")
        
        content_md = '\n'.join(new_lines)
    
    with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
        f.write(content_md)
    
    # 同步更新向量索引
    os.system(f"cd {MEMORY_DIR} && python3 memory.py index 2>/dev/null")
    
    # 检查存储
    os.system(f"python3 {MEMORY_DIR}/storage_monitor.py 2>/dev/null")

def search(query):
    """搜索记忆"""
    os.system(f"cd {MEMORY_DIR} && python3 memory.py search {query}")

def main():
    import sys
    
    if len(sys.argv) < 2:
        print("用法:")
        print("  memory.py add 对话 <内容>")
        print("  memory.py add 操作 <内容>")
        print("  memory.py search <关键词>")
        return
    
    if sys.argv[1] == "add" and len(sys.argv) >= 4:
        record_type = sys.argv[2]
        content = " ".join(sys.argv[3:])
        add_record(record_type, content)
        print(f"✓ 已记录: [{record_type}] {content}")
    elif sys.argv[1] == "search" and len(sys.argv) >= 3:
        query = " ".join(sys.argv[2:])
        search(query)
    else:
        print("参数错误")

if __name__ == "__main__":
    main()
