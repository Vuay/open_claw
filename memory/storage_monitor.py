#!/usr/bin/env python3
"""
存储监控脚本 - 监控记忆库大小
限制: 20GB
"""

import os
import sys
from pathlib import Path

MEMORY_DIR = Path("/root/.openclaw/workspace/memory")
MAX_SIZE_GB = 20
MAX_SIZE_BYTES = MAX_SIZE_GB * 1024 * 1024 * 1024

def get_dir_size(path):
    """获取目录大小"""
    total = 0
    for entry in os.scandir(path):
        if entry.is_file(follow_symlinks=False):
            total += entry.stat().st_size
        elif entry.is_dir(follow_symlinks=False):
            total += get_dir_size(entry.path)
    return total

def check_storage():
    """检查存储并返回状态"""
    if not MEMORY_DIR.exists():
        return {
            "exists": False,
            "size_gb": 0,
            "limit_gb": MAX_SIZE_GB,
            "percent": 0,
            "alert": False
        }
    
    size_bytes = get_dir_size(MEMORY_DIR)
    size_gb = size_bytes / (1024 * 1024 * 1024)
    percent = (size_bytes / MAX_SIZE_BYTES) * 100
    
    return {
        "exists": True,
        "size_bytes": size_bytes,
        "size_gb": round(size_gb, 2),
        "limit_gb": MAX_SIZE_GB,
        "percent": round(percent, 1),
        "alert": size_bytes > MAX_SIZE_BYTES
    }

def main():
    status = check_storage()
    
    if not status["exists"]:
        print("⚠️ 记忆目录不存在")
        sys.exit(1)
    
    print(f"📊 记忆库存储状态:")
    print(f"   当前大小: {status['size_gb']} GB")
    print(f"   限制大小: {status['limit_gb']} GB")
    print(f"   使用率: {status['percent']}%")
    
    if status["alert"]:
        print(f"\n🚨 警告: 记忆库已超过 {MAX_SIZE_GB}GB 限制!")
        print("   建议清理旧记忆或扩大存储限制")
        sys.exit(1)
    else:
        print(f"\n✅ 存储正常")
        sys.exit(0)

if __name__ == "__main__":
    main()
