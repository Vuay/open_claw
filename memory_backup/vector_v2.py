#!/usr/bin/env python3
"""
向量记忆系统 v2 - 使用 Sentence Transformers
语义搜索更精准
"""

import os
import json
from pathlib import Path
from sentence_transformers import SentenceTransformer

MEMORY_DIR = Path("/root/.openclaw/workspace/memory")
VECTOR_FILE = MEMORY_DIR / "vectors_v2.json"

# 轻量级模型
MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"

def load_model():
    """加载模型"""
    print(f"📥 加载模型: {MODEL_NAME}")
    return SentenceTransformer(MODEL_NAME)

def index_memories(model):
    """索引所有记忆文件"""
    vectors = {}
    
    files = list(MEMORY_DIR.glob("*.md"))
    files = [f for f in files if f.name not in ["vectors_v2.json", "vector_search.py"]]
    
    texts = []
    keys = []
    
    for md_file in files:
        content = md_file.read_text(encoding='utf-8')
        key = md_file.stem
        keys.append(key)
        texts.append(content)
    
    print(f"📚 正在索引 {len(texts)} 个文件...")
    embeddings = model.encode(texts, show_progress_bar=True)
    
    for i, key in enumerate(keys):
        vectors[key] = {
            "text": texts[i],
            "vector": embeddings[i].tolist(),
            "file": str(files[i])
        }
    
    VECTOR_FILE.write_text(json.dumps(vectors, ensure_ascii=False, indent=2))
    print(f"✓ 已索引 {len(vectors)} 个记忆文件")

def search_memories(model, query, top_k=3):
    """语义搜索记忆"""
    if not VECTOR_FILE.exists():
        print("🔄 首次索引...")
        index_memories(model)
    
    vectors = json.loads(VECTOR_FILE.read_text())
    
    # 查询向量
    query_vec = model.encode([query])[0].tolist()
    
    # 计算相似度
    from numpy import dot
    from numpy.linalg import norm
    
    results = []
    for key, data in vectors.items():
        v1 = query_vec
        v2 = data["vector"]
        score = dot(v1, v2) / (norm(v1) * norm(v2))
        
        results.append({
            "key": key,
            "file": data["file"],
            "score": float(score),
            "preview": data["text"][:300]
        })
    
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:top_k]

def main():
    import sys
    
    model = load_model()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "index":
            index_memories(model)
        elif sys.argv[1] == "search":
            query = " ".join(sys.argv[2:])
            print(f"\n🔍 搜索: {query}\n")
            results = search_memories(model, query)
            for r in results:
                print(f"【{r['key']}】相似度: {r['score']:.3f}")
                print("-" * 40)
                print(r['preview'])
                print("\n" + "=" * 40 + "\n")
        else:
            print("用法: memory_v2.py [index|search <关键词>]")
    else:
        index_memories(model)

if __name__ == "__main__":
    main()
