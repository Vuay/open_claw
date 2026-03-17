import os
import re
from collections import defaultdict

class LightKnowledgeBase:
    def __init__(self, doc_dir, index_dir):
        self.doc_dir = doc_dir
        self.index_dir = index_dir
        self.index_file = os.path.join(index_dir, 'knowledge.index')
        self.index = {}
        self.documents = {}
        self.load_index()
    
    def load_document(self, filepath):
        """加载文档"""
        ext = os.path.splitext(filepath)[1].lower()
        content = ""
        
        # TXT
        if ext == '.txt':
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        
        # PDF (轻量版)
        elif ext == '.pdf':
            try:
                import PyPDF2
                with open(filepath, 'rb') as f:
                    reader = PyPDF2.PdfReader(f)
                    for page in reader.pages[:10]:
                        content += page.extract_text() + "\n"
            except:
                pass
        
        # DOCX
        elif ext == '.docx':
            try:
                import docx
                doc = docx.Document(filepath)
                for para in doc.paragraphs:
                    content += para.text + "\n"
            except:
                pass
        
        return content[:50000]
    
    def load_index(self):
        """加载索引"""
        import json
        if os.path.exists(self.index_file):
            try:
                with open(self.index_file, 'r') as f:
                    data = json.load(f)
                    self.index = data.get('index', {})
                    self.documents = {}
            except:
                pass
    
    def build_index(self):
        """构建索引"""
        self.index = defaultdict(list)
        self.documents = {}
        
        if not os.path.exists(self.doc_dir):
            os.makedirs(self.doc_dir)
            return 0
        
        for filename in os.listdir(self.doc_dir):
            filepath = os.path.join(self.doc_dir, filename)
            if os.path.isfile(filepath):
                content = self.load_document(filepath)
                if content:
                    self.documents[filename] = content
                    words = re.findall(r'\w+', content.lower())
                    for word in set(words):
                        if len(word) > 2:
                            self.index[word].append(filename)
        
        # 保存索引
        import json
        with open(self.index_file, 'w') as f:
            json.dump({
                'index': dict(self.index),
                'documents': list(self.documents.keys())
            }, f)
        
        return len(self.documents)
    
    def search(self, query, top_k=3):
        """搜索"""
        query_words = set(re.findall(r'\w+', query.lower()))
        
        scores = defaultdict(float)
        for word in query_words:
            if word in self.index:
                for doc in self.index[word]:
                    scores[doc] += 1
        
        sorted_docs = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        results = []
        for doc, score in sorted_docs[:top_k]:
            results.append({
                'filename': doc,
                'score': score,
                'content': self.documents.get(doc, '')[:1000]
            })
        
        return results

if __name__ == "__main__":
    kb = LightKnowledgeBase(
        doc_dir="/root/.openclaw/knowledge/documents",
        index_dir="/root/.openclaw/knowledge/index"
    )
    count = kb.build_index()
    print(f"已索引 {count} 个文档")
    
    results = kb.search("OpenClaw")
    for r in results:
        print(f"- {r['filename']} (分数: {r['score']})")
