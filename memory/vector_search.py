#!/usr/bin/env python3
"""
简易向量记忆系统
使用词哈希平均作为简易语义向量
"""

import os
import json
import hashlib
import math
from pathlib import Path

MEMORY_DIR = Path("/root/.openclaw/workspace/memory")
VECTOR_FILE = MEMORY_DIR / "vectors.json"

def text_to_vector(text):
    """将文本转换为语义向量 (词哈希平均)"""
    words = text.lower().split()
    if not words:
        return [0] * 256
    
    vectors = []
    for word in words:
        # 使用MD5哈希生成固定向量
        h = hashlib.md5(word.encode()).hexdigest()
        vec = [int(c, 16) / 15.0 for c in h[:64]]  # 取前64个字符，转为0-1
        vectors.append(vec)
    
    # 平均所有词向量
    result = [0] * 64
    for vec in vectors:
        for i, v in enumerate(vec):
            result[i] += v
    return [v / len(vectors) for v in result]

def cosine_similarity(a, b):
    """计算余弦相似度"""
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0 or norm_b == 0:
        return 0
    return dot / (norm_a * norm_b)

def index_memories():
    """索引所有记忆文件"""
    vectors = {}
    
    for md_file in MEMORY_DIR.glob("*.md"):
        if md_file.name == "vectors.json":
            continue
            
        content = md_file.read_text(encoding='utf-8')
        # 提取标题作为key
        key = md_file.stem
        
        vectors[key] = {
            "text": content,
            "vector": text_to_vector(content),
            "file": str(md_file)
        }
    
    VECTOR_FILE.write_text(json.dumps(vectors, ensure_ascii=False, indent=2))
    print(f"✓ 已索引 {len(vectors)} 个记忆文件")

def search_memories(query, top_k=3):
    """语义搜索记忆"""
    if not VECTOR_FILE.exists():
        index_memories()
    
    vectors = json.loads(VECTOR_FILE.read_text())
    query_vec = text_to_vector(query)
    
    results = []
    for key, data in vectors.items():
        sim = cosine_similarity(query_vec, data["vector"])
        results.append({
            "key": key,
            "file": data["file"],
            "score": sim,
            "preview": data["text"][:200]
        })
    
    # 按相似度排序
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:top_k]

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "index":
            index_memories()
        elif sys.argv[1] == "search":
            query = " ".join(sys.argv[2:])
            results = search_memories(query)
            for r in results:
                print(f"\n[{r['key']}] 相似度: {r['score']:.2f}")
                print(r['preview'])
        else:
            print("用法: memory.py [index|search <关键词>]")
    else:
        # 默认执行索引
        index_memories()
