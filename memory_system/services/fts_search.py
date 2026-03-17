import sqlite3

class FTSSearch:
    def __init__(self, db_path='/root/.openclaw/memory_system/data/memory.db'):
        self.db_path = db_path
        self.init_fts()
    
    def init_fts(self):
        """初始化FTS5表"""
        conn = sqlite3.connect(self.db_path)
        
        # 创建FTS5虚拟表
        conn.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS memory_fts USING fts5(
            id,
            title,
            message,
            tokenize='porter unicode61'
        )
        """)
        
        # 创建触发器 - 插入时同步
        conn.execute("""
        CREATE TRIGGER IF NOT EXISTS memory_ai AFTER INSERT ON conversation BEGIN
            INSERT INTO memory_fts(id, title, message)
            VALUES (new.id, new.title, new.message);
        END
        """)
        
        # 创建触发器 - 删除时同步
        conn.execute("""
        CREATE TRIGGER IF NOT EXISTS memory_ad AFTER DELETE ON conversation BEGIN
            INSERT INTO memory_fts(memory_fts, id, title, message)
            VALUES ('delete', old.id, old.title, old.message);
        END
        """)
        
        # 重建索引
        conn.execute("INSERT INTO memory_fts(memory_fts) VALUES('rebuild')")
        
        conn.close()
        print("FTS5 initialized successfully")
    
    def search(self, query, limit=10):
        """FTS5搜索"""
        if not query:
            return []
        
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA cache_size = 2000")
        
        cursor = conn.execute("""
        SELECT id, title, 
            snippet(message, 0, '<mark>', '</mark>', 30) as snippet,
            bm25(memory_fts) as rank
        FROM memory_fts
        WHERE memory_fts MATCH ?
        ORDER BY rank
        LIMIT ?
        """, (query, limit))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'id': row[0],
                'title': row[1],
                'snippet': row[2],
                'rank': row[3]
            })
        
        conn.close()
        return results
