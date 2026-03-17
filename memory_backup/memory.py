#!/usr/bin/env python3
"""
向量记忆系统 - 使用 TF-IDF
"""

import json
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

MEMORY_DIR = Path("/root/.openclaw/workspace/memory")
VECTOR_FILE = MEMORY_DIR / "vectors_v3.json"

def index_memories():
    """索引所有记忆文件"""
    files = list(MEMORY_DIR.glob("*.md"))
    files = [f for f in files if f.name not in ["vectors_v3.json", "vector_search.py", "vector_v2.py", "memory.py"]]
    
    texts = []
    keys = []
    
    for md_file in files:
        content = md_file.read_text(encoding='utf-8')
        key = md_file.stem
        keys.append(key)
        texts.append(content)
    
    if not texts:
        print("⚠️ 没有找到记忆文件")
        return
    
    vectorizer = TfidfVectorizer(max_features=5000)
    embeddings = vectorizer.fit_transform(texts).toarray()
    
    vectors = {}
    for i, key in enumerate(keys):
        vectors[key] = {
            "text": texts[i],
            "vector": [float(x) for x in embeddings[i]],
            "file": str(files[i])
        }
    
    data = {
        "vectors": vectors,
        "vocabulary": {k: int(v) for k, v in vectorizer.vocabulary_.items()},
        "idf": [float(x) for x in vectorizer.idf_]
    }
    
    VECTOR_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2))
    print(f"✓ 已索引 {len(vectors)} 个记忆文件")

def search_memories(query, top_k=3):
    """语义搜索记忆"""
    if not VECTOR_FILE.exists():
        print("🔄 首次索引...")
        index_memories()
    
    with open(VECTOR_FILE, 'r') as f:
        data = json.load(f)
    
    vectors = data["vectors"]
    
    # 获取所有文本用于训练vectorizer
    all_texts = [vectors[k]["text"] for k in vectors]
    
    # 重新训练vectorizer
    vectorizer = TfidfVectorizer(max_features=5000)
    vectorizer.fit(all_texts)
    
    # 转换查询
    query_vec = vectorizer.transform([query]).toarray()[0]
    
    results = []
    for key, vec_data in vectors.items():
        v2 = np.array(vec_data["vector"])
        score = np.dot(query_vec, v2) / (np.linalg.norm(query_vec) * np.linalg.norm(v2) + 1e-10)
        
        results.append({
            "key": key,
            "file": vec_data["file"],
            "score": float(score),
            "preview": vec_data["text"][:400]
        })
    
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:top_k]

def main():
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "index":
            index_memories()
        elif sys.argv[1] == "search":
            query = " ".join(sys.argv[2:])
            print(f"\n🔍 搜索: {query}\n")
            results = search_memories(query)
            for r in results:
                print(f"【{r['key']}】相似度: {r['score']:.3f}")
                print("-" * 40)
                print(r['preview'])
                print("\n" + "=" * 40 + "\n")
        else:
            print("用法: memory.py [index|search <关键词>]")
    else:
        index_memories()

if __name__ == "__main__":
    main()
