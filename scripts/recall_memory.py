#!/usr/bin/env python3
"""记忆召回工具"""
import requests
import json
import sys

API_URL = "http://127.0.0.1:2323/api/memory/query"

def recall(query):
    try:
        resp = requests.post(API_URL, json={"query": query, "limit": 3}, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            return data.get("context", "")
    except:
        pass
    return ""

if __name__ == "__main__":
    query = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else ""
    print(recall(query))
