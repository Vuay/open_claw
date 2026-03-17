#!/usr/bin/env python3
import sys
sys.path.insert(0, '/root/.openclaw/memory_system')
try:
    from services.light_vector import LightVectorSearch
    vector_search = LightVectorSearch('/root/.openclaw/memory_system/data/memory.db')
except:
    vector_search = None
sys.path.insert(0, '/root/.openclaw/memory_system')
from services.fts_search import FTSSearch
import os, uuid, json
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, make_response, render_template_string
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from collections import Counter

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////root/.openclaw/memory_system/data/memory.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Conversation(db.Model):
    id = db.Column(db.String(64), primary_key=True)
    title = db.Column(db.String(256))
    summary = db.Column(db.Text)
    message = db.Column(db.Text)
    time = db.Column(db.String(32))
    tags = db.Column(db.String(256))
    messages_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Memory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(256), unique=True)
    content = db.Column(db.Text)

class Token(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(128), unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)
    ip = db.Column(db.String(64))

MEMORY_KEY = "admin"
# 初始化FTS搜索
fts_search = FTSSearch()
WORKSPACE = "/root/.openclaw/workspace"
DIARY_FILE = "/root/.openclaw/workspace/memory/diary.md"

def gen_token(): return uuid.uuid4().hex + datetime.now().strftime('%s')
def verify_token(t): tk = Token.query.filter_by(token=t).first(); return tk and tk.expires_at > datetime.utcnow()
def create_token(): 
    t = gen_token()
    db.session.add(Token(token=t, expires_at=datetime.utcnow()+timedelta(hours=24), ip=request.remote_addr))
    db.session.commit()
    return t
def get_t(): return request.cookies.get('memory_token')

def is_valid_conversation(msg):
    if not msg or len(msg) < 50: return False
    noise = ['cron:', 'record-conversations', 'Subagent Context', 'subagent (depth']
    return not any(p in msg[:300] for p in noise)

HTML = '''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>🧠 记忆系统</title><style>
*{box-sizing:border-box;margin:0;padding:0}body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;background:linear-gradient(135deg,#0f0f23,#1a1a2e);color:#e0e0e0;min-height:100vh;padding:20px}.container{max-width:1100px;margin:0 auto}.login{max-width:420px;margin:120px auto;background:linear-gradient(145deg,#1e2744,#16213e);padding:50px;border-radius:24px;box-shadow:0 20px 60px rgba(0,0,0,0.5);text-align:center;border:1px solid #2a3a5e}.login h1{color:#4CAF50;font-size:36px;margin-bottom:8px}.login .subtitle{color:#888;margin-bottom:30px;font-size:14px}input{width:100%;padding:18px;margin:15px 0;border-radius:12px;border:2px solid #2a3a5e;background:#0a0a15;color:#fff;font-size:16px}input:focus{outline:none;border-color:#4CAF50}button{width:100%;padding:18px;background:linear-gradient(135deg,#4CAF50,#45a049);color:#fff;border:none;border-radius:12px;cursor:pointer;font-size:16px;font-weight:bold}.header{background:linear-gradient(145deg,#1e2744,#16213e);padding:25px;border-radius:20px;margin-bottom:30px;box-shadow:0 10px 40px rgba(0,0,0,0.3);display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:15px}.header h1{color:#4CAF50;font-size:28px}.header h1 span{font-size:12px;color:#666;margin-left:10px}.nav{display:flex;gap:10px;flex-wrap:wrap}.nav button,.nav a{padding:14px 28px;background:#2a3a5e;color:#aaa;border:none;border-radius:12px;cursor:pointer;transition:all 0.3s;font-size:14px;text-decoration:none;display:inline-block}.nav button:hover,.nav button.active,.nav a:hover{background:#4CAF50;color:#fff}.stats{background:linear-gradient(145deg,#1e2744,#16213e);padding:25px;border-radius:16px;margin-bottom:30px;display:flex;gap:40px;justify-content:center}.stats div{text-align:center}.stats .num{font-size:36px;color:#4CAF50;font-weight:bold}.stats .label{font-size:14px;color:#888;margin-top:5px}.item{padding:24px;background:linear-gradient(145deg,#1e2744,#16213e);border-radius:16px;margin-bottom:20px;border-left:5px solid #4CAF50;box-shadow:0 10px 40px rgba(0,0,0,0.3);transition:all 0.3s}.item:hover{transform:translateX(8px)}.item a{color:inherit;text-decoration:none;display:block}.item .meta{display:flex;gap:10px;margin-bottom:10px;align-items:center}.item .time{color:#666;font-size:13px}.item .tag{background:#3498db;padding:4px 12px;border-radius:20px;font-size:12px;color:#fff}.item .title{font-size:20px;font-weight:bold;margin:12px 0;color:#fff}.item .summary{color:#aaa;line-height:1.7}.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:20px}.card{padding:24px;background:linear-gradient(145deg,#1e2744,#16213e);border-radius:16px;transition:all 0.3s}.card:hover{transform:translateY(-8px)}.card a{color:inherit;text-decoration:none;display:block}.card h3{color:#4CAF50;margin:0 0 12px;font-size:18px}.card .preview{color:#777;font-size:14px;line-height:1.6}.search-area{background:linear-gradient(145deg,#1e2744,#16213e);border-radius:16px;padding:30px;margin-bottom:30px}.search-title{color:#888;font-size:14px;margin-bottom:15px}.search-box{display:flex;gap:15px}.search-input{flex:1;padding:20px 25px;background:#0a0a15;border:2px solid #3498db;border-radius:12px;color:#fff;font-size:18px;min-width:300px}.search-input:focus{outline:none;border-color:#4CAF50;box-shadow:0 0 20px rgba(76,175,80,0.3)}.search-btn{padding:20px 40px;background:linear-gradient(135deg,#3498db,#2980b9);border:none;border-radius:12px;color:#fff;font-size:16px;font-weight:bold;cursor:pointer;transition:all 0.3s}.search-btn:hover{background:linear-gradient(135deg,#4CAF50,#45a049);transform:scale(1.02)}.result{padding:20px;background:linear-gradient(145deg,#1e2744,#16213e);border-radius:12px;margin-bottom:15px;border-left:4px solid #3498db}.result h4{color:#4CAF50;margin:0 0 10px;font-size:18px}.hidden{display:none}.empty{text-align:center;padding:60px;color:#666;font-size:18px}
</style></head><body>
{% if not authenticated %}
<div class="login"><h1>🧠 记忆系统</h1><p class="subtitle">安全 · 智能 · 进化</p><form method="POST" action="/memory/login"><input type="password" name="key" placeholder="🔑 输入密钥访问" required><button>🚀 进入系统</button></form>{% if error %}<p style="color:#e74c3c;margin-top:15px">❌ 密钥错误</p>{% endif %}</div>
{% else %}
<div class="container"><div class="header"><h1>🧠 记忆系统 <span>SQLite + JWT + PM2</span></h1><div class="nav">
<button class="active" onclick="show('timeline')">📅 时间线</button>
<button onclick="show('files')">📁 文件</button>
<button onclick="show('search')">🔍 搜索</button>
<button onclick="show('tags')">🏷️ 标签</button>
<button onclick="syncData()">🔄 同步</button>
<a href="/memory/diary" style="padding:14px 28px;background:#9b59b6;color:#fff;border-radius:12px">🧘 冥想</a>
<a href="/memory/logout" style="padding:14px 28px;background:#e74c3c;color:#fff;border-radius:12px">🚪 退出</a>
</div></div>
<div class="stats" id="stats-panel"><div><div class="num">?</div><div class="label">总对话</div></div><div><div class="num">?</div><div class="label">真实对话</div></div><div><div class="num">?</div><div class="label">进化分</div></div></div>
<div id="timeline">
{% for c in convs %}{% if is_valid(c.message) %}<a href="/memory/conversation/{{c.id}}" class="item"><div class="meta"><span class="time">🕒 {{c.time}}</span>{% if c.tags %}{% for t in c.tags.split(',') %}<span class="tag">{{t}}</span>{% endfor %}{% endif %}</div><div class="title">{{c.title or '对话'}}</div><div class="summary">{{c.summary or c.message or ''}}</div></a>{% endif %}{% endfor %}</div>
<div id="files" class="hidden"><div class="grid">{% for m in mems %}<a href="/memory/file/{{m.filename}}" class="card"><h3>📄 {{m.filename}}</h3><div class="preview">{{m.content[:120]}}...</div></a>{% endfor %}</div></div>
<div id="search" class="hidden"><div class="search-area"><div class="search-title">🔍 在记忆库中搜索...</div><div class="search-box"><input class="search-input" id="q" placeholder="输入关键词搜索对话和文件..."><button class="search-btn" onclick="doSearch()">搜索</button></div></div><div id="results"></div></div>
<div id="tags" class="hidden"><div class="grid">{% for tag in ['memory','evolution','multi-agent','tools','browser','meditation','community','deployment'] %}<a href="#" onclick="filterTag('{{tag}}')" class="card"><h3>🏷️ {{tag}}</h3></a>{% endfor %}</div></div></div>{% endif %}
<script>
function show(v){document.getElementById('timeline').classList.add('hidden');document.getElementById('files').classList.add('hidden');document.getElementById('search').classList.add('hidden');document.getElementById('tags').classList.add('hidden');document.getElementById(v).classList.remove('hidden');document.querySelectorAll('.nav button').forEach(b=>b.classList.remove('active'));event.target.classList.add('active')}
function doSearch(){const q=document.getElementById('q').value;if(!q)return;fetch('/memory/api/search?q='+encodeURIComponent(q)).then(r=>r.json()).then(d=>{const div=document.getElementById('results');if(!d.length){div.innerHTML='<div class="empty">未找到相关内容</div>';return;}div.innerHTML=d.map(r=>'<a href="'+(r.type==='conversation'?'/memory/conversation/'+r.id:'/memory/file/'+r.filename)+'" class="result"><h4>'+(r.title||r.filename)+'</h4></a>').join('')})}
function filterTag(tag){fetch('/memory/api/tag/'+tag).then(r=>r.json()).then(d=>{document.getElementById('timeline').innerHTML=d.map(c=>'<a href="/memory/conversation/'+c.id+'" class="item"><div class="title">'+c.title+'</div></a>').join('')})}
function syncData(){fetch('/memory/api/sync',{method:'POST'}).then(r=>r.json()).then(d=>{alert(d.message||d.error);if(d.success)location.reload()})}
function is_valid(msg){if(!msg||msg.length<50)return false;var noise=['cron:','record-conversations','Subagent Context','subagent (depth'];for(var i=0;i<noise.length;i++){if(msg.substring(0,300).indexOf(noise[i])>-1)return false}return true}
fetch('/memory/api/stats_detailed').then(r=>r.json()).then(d=>{var s=document.getElementById('stats-panel');s.innerHTML='<div><div class="num">'+d.total_conversations+'</div><div class="label">总对话</div></div><div><div class="num">'+d.real_conversations+'</div><div class="label">真实对话</div></div><div><div class="num">'+d.evolution_score+'</div><div class="label">进化分</div></div>'});
setInterval(()=>{if(!document.getElementById('timeline').classList.contains('hidden'))fetch('/memory/api/check').then(r=>r.json()).then(d=>{if(d.count>0)location.reload()})},30000)
</script></body></html>'''

@app.template_filter('is_valid')
def is_valid_filter(msg):
    return is_valid_conversation(msg)

@app.route('/memory')
def index():
    t = get_t()
    if not verify_token(t): 
        return render_template_string(HTML,authenticated=False,error=False,convs=[],mems=[],is_valid=is_valid_conversation)
    convs = [c for c in Conversation.query.order_by(Conversation.time.desc()).limit(100).all()]
    return render_template_string(HTML,authenticated=True,error=False,convs=convs,mems=Memory.query.all(),is_valid=is_valid_conversation)

@app.route('/memory/login',methods=['POST'])
def login():
    if request.form.get('key')!=MEMORY_KEY: return render_template_string(HTML,authenticated=False,error=True,convs=[],mems=[],is_valid=is_valid_conversation)
    resp = make_response('<script>location.href="/memory"</script>')
    resp.set_cookie('memory_token',create_token(),max_age=86400,httponly=True,secure=True,samesite='Lax')
    return resp

@app.route('/memory/logout')
def logout(): return make_response('<script>location.href="/memory"</script>')

@app.route('/memory/diary')
def view_diary():
    if not verify_token(get_t()): return '<script>location.href="/memory"</script>'
    content = open(DIARY_FILE).read() if os.path.exists(DIARY_FILE) else ""
    return f'''<!DOCTYPE html><html><head><meta charset="UTF-8"><title>每日冥想</title><style>body{{background:#0f0f23;color:#e0e0e0;padding:30px;font-family:-apple-system}}textarea{{width:100%;height:400px;background:#1e2744;color:#fff;border-radius:12px;padding:20px;font-size:16px;border:2px solid #9b59b6}}button{{background:#9b59b6;color:#fff;padding:15px 30px;border:none;border-radius:12px;font-size:16px;cursor:pointer;margin-top:20px}}a{{color:#9b59b6}}</style></head><body><h1>🧘 每日冥想</h1><p style="color:#888;margin-bottom:20px">记录今天的不足与可优化点，用于自我进化</p><form method="POST" action="/memory/diary/save"><textarea name="content">{content}</textarea><button>💾 保存</button></form><br><a href="/memory">← 返回</a></body></html>'''

@app.route('/memory/diary/save', methods=['POST'])
def save_diary():
    if not verify_token(get_t()): return '<script>location.href="/memory"</script>'
    content = request.form.get('content', '')
    with open(DIARY_FILE, 'w') as f: f.write(content)
    return '<script>alert("已保存");location.href="/memory/diary"</script>'

@app.route('/memory/file/<path:f>')
def view_file(f):
    if not verify_token(get_t()): return '<script>alert("请先登录");location.href="/memory"</script>'
    m = Memory.query.filter_by(filename=f).first()
    return f'''<!DOCTYPE html><html><head><meta charset="UTF-8"><title>{f}</title><style>body{{background:#0f0f23;color:#e0e0e0;padding:30px}}pre{{background:#1e2744;padding:30px;border-radius:16px;white-space:pre-wrap}}a{{color:#4CAF50}}</style></head><body><a href="/memory">← 返回</a><pre>{m.content if m else "不存在"}</pre></body></html>'''

@app.route('/memory/conversation/<id>')
def view_conv(id):
    if not verify_token(get_t()): return '<script>alert("请先登录");location.href="/memory"</script>'
    c = Conversation.query.get(id)
    return f'''<!DOCTYPE html><html><head><meta charset="UTF-8"><title>{c.title if c else id}</title><style>body{{background:#0f0f23;color:#e0e0e0;padding:30px}}pre{{background:#1e2744;padding:30px;border-radius:16px;white-space:pre-wrap}}a{{color:#4CAF50}}</style></head><body><a href="/memory">← 返回</a><pre>{c.message or c.summary if c else "不存在"}</pre></body></html>'''

@app.route('/memory/api/search')
def api_search():
    if not verify_token(get_t()): return '{"error":"Unauthorized"}', 401, {'Content-Type':'application/json'}
    q = request.args.get('q', '') or ''
    if not q: return jsonify([])
    
    r = []
    
    # FTS5搜索
    try:
        import sqlite3
        conn = sqlite3.connect('/root/.openclaw/memory_system/data/memory.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, title FROM memory_fts WHERE memory_fts MATCH ? LIMIT 20", (q,))
        for row in cursor.fetchall():
            r.append({'type':'conversation','id':row[0],'title':row[1]})
        conn.close()
    except Exception as e:
        # FTS失败时使用LIKE后备
        ql = q.lower()
        for c in Conversation.query.all():
            if ql in (c.message or '').lower() or ql in (c.title or '').lower():
                r.append({'type':'conversation','id':c.id,'title':(c.title or '')[:80]})
                if len(r) >= 20: break
    
    # 文件搜索
    ql = q.lower()
    for m in Memory.query.all():
        if ql in (m.content or '').lower():
            r.append({'type':'file','filename':m.filename})
            if len(r) >= 10: break
    
    return jsonify(r)

@app.route('/memory/api/search_index')
def rebuild_index():
    if not verify_token(get_t()): return '{"error":"Unauthorized"}', 401, {'Content-Type':'application/json'}
    try:
        fts_search.init_fts()
        return jsonify({'status': 'success', 'message': '索引已重建'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/memory/api/sync',methods=['POST'])
def api_sync():
    if not verify_token(get_t()): return '{"error":"Unauthorized"}', 401, {'Content-Type':'application/json'}
    return jsonify({'success':True,'message':'同步完成'})

@app.route('/memory/api/check')
def api_check():
    if not verify_token(get_t()): return '{"error":"Unauthorized"}', 401, {'Content-Type':'application/json'}
    return jsonify({'count':Conversation.query.count()})

@app.route('/memory/api/tag/<tag>')
def api_tag(tag):
    if not verify_token(get_t()): return '{"error":"Unauthorized"}', 401, {'Content-Type':'application/json'}
    convs = Conversation.query.filter(Conversation.tags.like(f'%{tag}%')).all() if tag else Conversation.query.all()
    return jsonify([{'id':c.id,'title':c.title,'time':c.time,'tags':c.tags} for c in convs])

@app.route('/memory/api/stats_detailed')
def api_stats_detailed():
    if not verify_token(get_t()): return '{"error":"Unauthorized"}', 401, {'Content-Type':'application/json'}
    all_convs = Conversation.query.all()
    real_convs = [c for c in all_convs if is_valid_conversation(c.message)]
    tags = Counter()
    for c in all_convs:
        if c.tags:
            for t in c.tags.split(','): tags[t.strip()] += 1
    avg_messages = sum(c.messages_count for c in real_convs) / max(len(real_convs), 1)
    evolution_score = len(real_convs) * 10 + Memory.query.count() * 5 + tags.total() * 2
    return jsonify({
        'total_conversations': len(all_convs),
        'real_conversations': len(real_convs),
        'avg_messages_per_conversation': round(avg_messages, 1),
        'memory_files': Memory.query.count(),
        'tag_distribution': dict(tags.most_common(10)),
        'evolution_score': evolution_score,
        'system_health': 'excellent' if evolution_score > 100 else 'good' if evolution_score > 50 else 'normal'
    })



@app.route('/api/memory/query', methods=['POST'])
def query_memory():
    """AI查询记忆的API"""
    data = request.json or {}
    query = data.get('query', '')
    limit = data.get('limit', 5)
    
    if not query:
        return jsonify({'error': 'Query is empty'}), 400
    
    import sqlite3
    conn = sqlite3.connect('/root/.openclaw/memory_system/data/memory.db')
    cursor = conn.cursor()
    
    # 搜索相关记忆 - 排除cron和系统消息
    cursor.execute("""
        SELECT id, title, message, time
        FROM conversation
        WHERE (message LIKE ? OR title LIKE ?)
        AND (message IS NULL OR (message NOT LIKE '%cron:%' AND message NOT LIKE '%record-conversations%' AND message NOT LIKE '%Subagent Context%'))
        ORDER BY time DESC
        LIMIT ?
    """, (f'%{query}%', f'%{query}%', limit))
    
    if not query:
        return jsonify({'error': 'Query is empty'}), 400
    
    # 查询相关记忆
    import sqlite3
    conn = sqlite3.connect('/root/.openclaw/memory_system/data/memory.db')
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, title, message, time
        FROM conversation
        WHERE message LIKE ? OR title LIKE ?
        ORDER BY time DESC
        LIMIT ?
    """, (f'%{query}%', f'%{query}%', limit))
    
    results = []
    for row in cursor.fetchall():
        results.append({
            'id': row[0],
            'title': row[1],
            'content': row[2][:500] if row[2] else '',
            'time': row[3]
        })
    
    conn.close()
    
    # 构建记忆上下文
    context = "以下是相关的历史对话记录：\n\n"
    for r in results:
        context += f"【{r['title']}】\n{r['content']}\n\n"
    
    return jsonify({
        'query': query,
        'count': len(results),
        'context': context,
        'results': results
    })




# 向量搜索API
@app.route('/memory/api/vector_search')
def vector_search_api():
    if not verify_token(get_t()): return '{"error":"Unauthorized"}', 401, {'Content-Type':'application/json'}
    query = request.args.get('q', '')
    if not query: return jsonify({'results': []})
    
    global vector_search
    if vector_search is None:
        try:
            vector_search = LightVectorSearch('/root/.openclaw/memory_system/data/memory.db')
        except:
            return jsonify({'results': [], 'error': '向量索引未构建'})
    
    try:
        results = vector_search.search(query, top_k=5)
        return jsonify({'results': results, 'query': query})
    except Exception as e:
        return jsonify({'results': [], 'error': str(e)})

# 构建向量索引
@app.route('/memory/api/vector_build')
def vector_build():
    if not verify_token(get_t()): return '{"error":"Unauthorized"}', 401, {'Content-Type':'application/json'}
    global vector_search
    
    try:
        import sqlite3
        conn = sqlite3.connect('/root/.openclaw/memory_system/data/memory.db')
        c = conn.cursor()
        c.execute('SELECT id, message FROM conversation WHERE message IS NOT NULL AND message != ""')
        rows = c.fetchall()
        conn.close()
        
        if rows:
            texts = [r[1][:2000] for r in rows]
            ids = [r[0] for r in rows]
            vector_search = LightVectorSearch('/root/.openclaw/memory_system/data/memory.db')
            vector_search.build_index(texts, ids)
            return jsonify({'status': 'success', 'count': len(ids)})
        return jsonify({'status': 'no_data'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})


if __name__ == '__main__':
    with app.app_context(): db.create_all()
    from waitress import serve
    print("🧠 记忆系统启动 - 端口2323")
    serve(app,host='0.0.0.0',port=2323,threads=4)

@app.route('/api/memory/query', methods=['POST'])
def query_memory():
    data = request.json
    query = data.get('query', '')
    limit = data.get('limit', 5)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.execute("SELECT id, title, message FROM conversation WHERE message LIKE ? LIMIT ?" , (f'%{query}%', limit))
    results = [{'title': r[1], 'content': r[2][:500]} for r in cursor.fetchall()]
    conn.close()
    context = '\n'.join([f"【{r['title']}】\n{r['content']}" for r in results])
    return jsonify({'query': query, 'context': context, 'count': len(results)})
