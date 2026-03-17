import uuid
#!/usr/bin/env python3
"""
记忆系统 Web 服务 - 简洁版
"""
import os
import json
from datetime import datetime, timedelta
from flask import Flask, request, render_template_string, jsonify, make_response
from waitress import serve

app = Flask(__name__)

# 配置
MEMORY_KEY = "miao669"
TOKEN_EXPIRE_HOURS = 24 * 7
WORKSPACE = "/root/.openclaw/workspace"
MEMORY_FILE = os.path.join(WORKSPACE, "MEMORY.md")
DIARY_DIR = os.path.join(WORKSPACE, "memory")
CONVERSATIONS_FILE = os.path.join(WORKSPACE, "memory/conversations.json")

tokens = {}

def generate_token():
    return uuid.uuid4().hex

def verify_token(token):
    if not token or token not in tokens:
        return False
    if datetime.now() > tokens[token]['expire']:
        del tokens[token]
        return False
    return True

def verify_key(key):
    if key != MEMORY_KEY:
        return None
    token = generate_token()
    tokens[token] = {'expire': datetime.now() + timedelta(hours=TOKEN_EXPIRE_HOURS)}
    return token

def get_token_from_request():
    return request.cookies.get('memory_token')

def read_memory_files():
    files = {}
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, 'r') as f:
            files['MEMORY.md'] = f.read()
    if os.path.exists(DIARY_DIR):
        for fname in sorted(os.listdir(DIARY_DIR)):
            if fname.endswith('.md') and fname != 'MEMORY.md':
                with open(os.path.join(DIARY_DIR, fname), 'r') as f:
                    files[f'memory/{fname}'] = f.read()
    return files

def read_conversations():
    convs = []
    if os.path.exists(CONVERSATIONS_FILE):
        try:
            with open(CONVERSATIONS_FILE, 'r') as f:
                data = json.load(f)
                convs = data.get('conversations', []) if isinstance(data, dict) else data
        except:
            convs = []
    return sorted(convs, key=lambda x: x.get('time', ''), reverse=True)

HTML = '''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>记忆系统</title>
    <style>
        * { box-sizing: border-box; }
        body { font-family: -apple-system, sans-serif; background: #1a1a2e; color: #eee; margin: 0; padding: 20px; }
        .container { max-width: 900px; margin: 0 auto; }
        
        .login { max-width: 400px; margin: 100px auto; text-align: center; background: #16213e; padding: 40px; border-radius: 16px; }
        .login h1 { color: #4CAF50; }
        .login input { width: 100%; padding: 14px; margin: 15px 0; border-radius: 8px; border: 2px solid #333; background: #0f0f23; color: #fff; font-size: 16px; }
        .login button { width: 100%; padding: 14px; background: #4CAF50; color: white; border: none; border-radius: 8px; cursor: pointer; font-size: 16px; font-weight: bold; }
        
        .header { display: flex; justify-content: space-between; align-items: center; padding: 20px 0; border-bottom: 1px solid #333; margin-bottom: 20px; }
        .header h1 { color: #4CAF50; }
        .nav { display: flex; gap: 10px; }
        .nav button { padding: 10px 20px; background: #333; color: #fff; border: none; border-radius: 8px; cursor: pointer; }
        .nav button:hover, .nav button.active { background: #4CAF50; }
        
        .timeline-item { margin-bottom: 20px; padding: 20px; background: linear-gradient(135deg, #16213e 0%, #1a2744 100%); border-radius: 12px; border-left: 4px solid #4CAF50; box-shadow: 0 4px 15px rgba(0,0,0,0.3); }
        .timeline-item a { text-decoration: none; color: inherit; display: block; }
        .timeline-item:hover { transform: translateY(-3px); }
        .time { color: #888; font-size: 13px; }
        .title { font-size: 18px; font-weight: bold; margin: 8px 0; }
        .summary { color: #aaa; line-height: 1.6; white-space: pre-wrap; }
        
        .files-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 16px; }
        .file-card { padding: 20px; background: #16213e; border-radius: 12px; text-decoration: none; color: inherit; display: block; }
        .file-card:hover { background: #1e2a4a; }
        .file-card h3 { color: #4CAF50; margin: 0 0 8px 0; }
        .file-card .preview { color: #888; font-size: 14px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
        
        .search-box { display: flex; gap: 10px; margin-bottom: 20px; }
        .search-box input { flex: 1; padding: 12px; border: none; border-radius: 8px; background: #16213e; color: #fff; font-size: 16px; }
        .search-box button { padding: 12px 24px; background: #4CAF50; color: white; border: none; border-radius: 8px; cursor: pointer; }
        
        .search-result { padding: 16px; background: #16213e; border-radius: 8px; margin-bottom: 12px; }
        .search-result h4 { color: #4CAF50; margin: 0 0 8px 0; }
        .search-result .match { color: #888; font-size: 14px; }
        
        .hidden { display: none; }
    </style>
</head>
<body>
    {% if not authenticated %}
    <div class="login">
        <h1>🧠 记忆系统</h1>
        <p>请输入密钥访问</p>
        <form method="POST" action="/memory/login">
            <input type="password" name="key" placeholder="请输入密钥" required>
            <button type="submit">进入</button>
        </form>
        {% if error %}<p style="color:red">密钥错误</p>{% endif %}
    </div>
    {% else %}
    <div class="container">
        <div class="header">
            <h1>🧠 记忆系统</h1>
            <div class="nav">
                <button class="active" onclick="showView('timeline')">时间线</button>
                <button onclick="showView('files')">文件</button>
                <button onclick="showView('search')">搜索</button>
                <a href="/memory/logout" style="padding:10px 20px;background:#333;color:#fff;border-radius:8px;text-decoration:none;">退出</a>
            </div>
        </div>
        
        <div id="timeline-view">
            {% for conv in conversations %}
            <a href="/memory/conversation/{{conv.id}}" class="timeline-item">
                <div class="time">{{conv.time}}</div>
                <div class="title">{{conv.title or '对话'}}</div>
                <div class="summary">{{conv.summary or conv.message or ''}}</div>
            </a>
            {% endfor %}
            {% if not conversations %}<p style="color:#888;text-align:center;">暂无对话记录</p>{% endif %}
        </div>
        
        <div id="files-view" class="hidden">
            <div class="files-grid">
                {% for fname, content in files.items() %}
                <a href="/memory/file/{{fname}}" class="file-card">
                    <h3>{{fname}}</h3>
                    <div class="preview">{{content[:100]}}...</div>
                </a>
                {% endfor %}
            </div>
        </div>
        
        <div id="search-view" class="hidden">
            <div class="search-box">
                <input type="text" id="search-input" placeholder="搜索记忆...">
                <button onclick="doSearch()">搜索</button>
            </div>
            <div id="search-results"></div>
        </div>
    </div>
    {% endif %}
    
    <script>
        function showView(view) {
            document.getElementById('timeline-view').classList.add('hidden');
            document.getElementById('files-view').classList.add('hidden');
            document.getElementById('search-view').classList.add('hidden');
            document.querySelectorAll('.nav button').forEach(b => b.classList.remove('active'));
            document.getElementById(view + '-view').classList.remove('hidden');
            event.target.classList.add('active');
        }
        
        // 自动刷新 - 每30秒刷新
        setInterval(() => {
            const tl = document.getElementById('timeline-view');
            if (tl && !tl.classList.contains('hidden')) location.reload();
        }, 30000);
        
        function doSearch() {
            const q = document.getElementById('search-input').value;
            if (!q) return;
            fetch('/memory/api/search?q=' + encodeURIComponent(q)).then(r=>r.json()).then(results => {
                const div = document.getElementById('search-results');
                if (!results.length) { div.innerHTML = '<p style="color:#888">未找到</p>'; return; }
                div.innerHTML = results.map(r => '<a href="/memory/file/'+encodeURIComponent(r.file)+'" class="search-result"><h4>'+r.file+'</h4>'+(r.matches||[]).map(m=>'<div class="match">...'+m.text+'...</div>').join('')+'</a>').join('');
            });
        }
    </script>
</body>
</html>
'''

@app.route('/memory')
def index():
    token = get_token_from_request()
    if not verify_token(token):
        return render_template_string(HTML, authenticated=False, error=False, files={}, conversations=[])
    files = read_memory_files()
    convs = read_conversations()
    return render_template_string(HTML, authenticated=True, error=False, files=files, conversations=convs[:20])

@app.route('/memory/login', methods=['POST'])
def login():
    key = request.form.get('key', '')
    token = verify_key(key)
    if not token:
        return render_template_string(HTML, authenticated=False, error=True, files={}, conversations=[])
    resp = make_response('<script>location.href="/memory"</script>')
    resp.set_cookie('memory_token', token, max_age=60*60*TOKEN_EXPIRE_HOURS, httponly=True, secure=True)
    return resp

@app.route('/memory/logout')
def logout():
    token = get_token_from_request()
    if token and token in tokens:
        del tokens[token]
    return make_response('<script>location.href="/memory"</script>')

@app.route('/memory/file/<path:filename>')
def view_file(filename):
    token = get_token_from_request()
    if not verify_token(token):
        return '<script>alert("请先登录");location.href="/memory"</script>'
    files = read_memory_files()
    content = files.get(filename, '文件不存在')
    return f'''<!DOCTYPE html><html><head><meta charset="UTF-8"><title>{filename}</title>
    <style>body{{background:#1a1a2e;color:#eee;padding:20px;font-family:sans-serif}}pre{{background:#16213e;padding:20px;border-radius:12px;white-space:pre-wrap}}</style></head>
    <body><a href="/memory" style="color:#4CAF50">←返回</a><h1>{filename}</h1><pre>{content}</pre></body></html>'''

@app.route('/memory/conversation/<conv_id>')
def view_conv(conv_id):
    token = get_token_from_request()
    if not verify_token(token):
        return '<script>alert("请先登录");location.href="/memory"</script>'
    convs = read_conversations()
    conv = next((c for c in convs if c.get('id') == conv_id), None)
    if not conv:
        return '<script>alert("对话不存在");location.href="/memory"</script>'
    return f'''<!DOCTYPE html><html><head><meta charset="UTF-8"><title>{conv.get('title','对话')}</title>
    <style>body{{background:#1a1a2e;color:#eee;padding:20px;font-family:sans-serif;max-width:800px;margin:0 auto}}
    .msg{{margin:20px 0;padding:20px;border-radius:12px}}
    .user{{background:linear-gradient(135deg,#1e3a5f,#2a4a6f)}}
    .assistant{{background:linear-gradient(135deg,#16213e,#1a2744)}}
    .role{{font-size:12px;opacity:0.7;margin-bottom:8px}}
    .user .role{{color:#4CAF50}}
    .assistant .role{{color:#e94560}}
    .content{{white-space:pre-wrap;line-height:1.8}}
    a{{color:#4CAF50}}</style></head>
    <body><a href="/memory">←返回</a><h1>💬 {conv.get('title','')}</h1>
    <div class="msg user"><div class="role">👤 用户</div><div class="content">{conv.get('message', conv.get('summary',''))}</div></div>
    </body></html>'''

@app.route('/memory/api/search')
def search():
    token = get_token_from_request()
    if not verify_token(token):
        return jsonify({'error':'Unauthorized'}), 401
    q = request.args.get('q','').lower()
    files = read_memory_files()
    results = []
    for fname, content in files.items():
        if q in content.lower():
            lines = content.split('\n')
            matches = [{'text':l.strip()[:100]} for l in lines if q in l.lower()][:5]
            results.append({'file':fname,'matches':matches})
    return jsonify(results)

if __name__ == '__main__':
    print("记忆系统启动，端口2323...")
    serve(app, host='0.0.0.0', port=2323, threads=4)
