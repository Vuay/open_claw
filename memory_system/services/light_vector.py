import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pickle
import os
import re

class LightVectorSearch:
    def __init__(self, db_path, index_path=None):
        self.db_path = db_path
        self.index_path = index_path or db_path.replace('.db', '_vector.pkl')
        # 使用字符级n-gram，更适合中英文混合
        self.vectorizer = TfidfVectorizer(
            max_features=5000, 
            ngram_range=(1, 3),  # 1-3 gram
            analyzer='char_wb',   # 字符级
            min_df=1
        )
        self.vectors = None
        self.ids = []
        self.load_index()
    
    def load_index(self):
        if os.path.exists(self.index_path):
            try:
                with open(self.index_path, 'rb') as f:
                    data = pickle.load(f)
                    self.vectors = data['vectors']
                    self.ids = data['ids']
                    if 'vectorizer' in data:
                        self.vectorizer = data['vectorizer']
            except Exception as e:
                print(f"Load index error: {e}")
                pass
    
    def build_index(self, texts, ids):
        self.ids = ids
        # 预处理文本
        processed = []
        for t in texts:
            # 保留英文和中文
            text = re.sub(r'[^\w\s\u4e00-\u9fff]', ' ', str(t))
            processed.append(text)
        
        self.vectors = self.vectorizer.fit_transform(processed)
        with open(self.index_path, 'wb') as f:
            pickle.dump({
                'vectors': self.vectors, 
                'ids': self.ids, 
                'vectorizer': self.vectorizer
            }, f)
    
    def search(self, query, top_k=5):
        if self.vectors is None or len(self.ids) == 0:
            return []
        
        # 预处理查询
        q = re.sub(r'[^\w\s\u4e00-\u9fff]', ' ', str(query))
        
        query_vec = self.vectorizer.transform([q])
        similarities = cosine_similarity(query_vec, self.vectors)[0]
        top_indices = similarities.argsort()[-top_k:][::-1]
        
        results = []
        for idx in top_indices:
            if similarities[idx] > 0.05:  # 降低阈值
                results.append({
                    'id': self.ids[idx], 
                    'score': float(similarities[idx])
                })
        return results
