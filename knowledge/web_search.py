import os
import time
from collections import defaultdict

class SecureWebSearch:
    def __init__(self):
        self.api_key = os.environ.get('SEARCH_API_KEY', 'YOUR_API_KEY')
        self.rate_limit = defaultdict(list)
        self.cache = {}
        self.cache_ttl = 300
    
    def verify_api_key(self, key):
        return key == self.api_key
    
    def check_rate_limit(self, api_key):
        if not api_key:
            api_key = 'anonymous'
        now = time.time()
        self.rate_limit[api_key] = [t for t in self.rate_limit[api_key] if now - t < 60]
        if len(self.rate_limit[api_key]) > 10:
            return False
        self.rate_limit[api_key].append(now)
        return True
    
    def get_cache(self, query):
        if query in self.cache:
            cached_time, cached_data = self.cache[query]
            if time.time() - cached_time < self.cache_ttl:
                return cached_data
        return None
    
    def set_cache(self, query, data):
        self.cache[query] = (time.time(), data)
    
    def search(self, query, api_key='', max_results=5):
        if not self.verify_api_key(api_key):
            return {'error': '认证失败'}
        
        if not self.check_rate_limit(api_key):
            return {'error': '请求过于频繁'}
        
        query = query[:150]
        
        cached = self.get_cache(query)
        if cached:
            return cached
        
        try:
            from ddgs import DDGS
            ddgs = DDGS()
            results = []
            for r in ddgs.text(query, max_results=max_results):
                results.append({
                    'title': r.get('title', ''),
                    'url': r.get('url', ''),
                    'snippet': r.get('body', '')[:200]
                })
            data = {'query': query, 'count': len(results), 'results': results}
            self.set_cache(query, data)
            return data
        except Exception as e:
            return {'error': str(e)[:80]}

web_search = SecureWebSearch()
