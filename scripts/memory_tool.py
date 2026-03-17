#!/usr/bin/env python3
"""记忆搜索工具 - 给OpenClaw调用"""
import requests
import json
import sys

MEMORY_API = "http://127.0.0.1:2323/api/memory/query"

def search_memory(query, limit=3):
    """搜索记忆并返回上下文"""
    try:
        response = requests.post(
            MEMORY_API,
            json={'query': query, 'limit': limit},
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            return data.get('context', '')
        else:
            return f"Error: {response.status_code}"
    except Exception as e:
        return f"Memory search error: {e}"

# 测试
if __name__ == "__main__":
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    else:
        query = "记忆系统"
    
    result = search_memory(query)
    print(result)
