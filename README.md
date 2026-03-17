# 🦞 OpenClaw 记忆系统部署配置

本仓库包含 OpenClaw 记忆系统的完整部署配置，支持一键部署到任意服务器。

## 📦 包含内容

| 目录 | 说明 |
|------|------|
| `.openclaw/` | OpenClaw配置 |
| `memory_system/` | Flask记忆系统Web应用 |
| `nginx/` | Nginx反向代理配置 |
| `scripts/` | 同步和召回脚本 |

---

## 🚀 一键部署

### 前提条件

- Ubuntu 20.04+ / Debian 11+ 服务器
- 已安装 Python 3.8+
- 已安装 Nginx
- root权限或sudo权限

### 快速部署

```bash
# 1. 克隆仓库
git clone https://github.com/Vuay/open_claw.git /root/open_claw
cd /root/open_claw

# 2. 安装依赖
pip3 install flask flask-sqlalchemy flask-cors requests

# 3. 安装PM2 (如果没有)
npm install -g pm2

# 4. 复制Nginx配置
sudo cp nginx/openclaw /etc/nginx/sites-available/
sudo ln -sf /etc/nginx/sites-available/openclaw /etc/nginx/sites-enabled/

# 5. 测试并重载Nginx
sudo nginx -t
sudo nginx -s reload

# 6. 启动记忆系统
cd memory_system
pm2 start app.py --name memory-system
pm2 save
pm2 startup
```

---

## 📝 详细部署步骤

### 步骤1: 克隆仓库

```bash
# 创建工作目录
mkdir -p /root/open_claw
cd /root/open_claw

# 克隆仓库
git clone https://github.com/Vuay/open_claw.git .
```

### 步骤2: 安装Python依赖

```bash
# 检查Python版本
python3 --version

# 安装pip (如果需要)
sudo apt update
sudo apt install -y python3-pip

# 安装依赖
pip3 install flask flask-sqlalchemy flask-cors requests

# 验证安装
pip3 list | grep -E "flask|requests"
```

### 步骤3: 安装Node.js和PM2

```bash
# 安装Node.js (如果没有)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# 安装PM2
sudo npm install -g pm2

# 验证安装
pm2 --version
```

### 步骤4: 配置Nginx

```bash
# 复制配置文件
sudo cp nginx/openclaw /etc/nginx/sites-available/openclaw

# 创建软链接
sudo ln -sf /etc/nginx/sites-available/openclaw /etc/nginx/sites-enabled/

# 检查配置
sudo nginx -t

# 重载Nginx
sudo nginx -s reload
```

### 步骤5: 启动记忆系统

```bash
cd memory_system

# 直接运行测试
python3 app.py

# 如果正常，用PM2守护
pm2 start app.py --name memory-system

# 保存PM2进程列表
pm2 save

# 设置开机自启
pm2 startup
```

### 步骤6: 配置OpenClaw (可选)

```bash
# 复制配置文件
cp .openclaw/openclaw.json ~/.openclaw/openclaw.json

# 编辑配置，添加你的API Key
nano ~/.openclaw/openclaw.json
```

---

## 🔐 修改密钥

### 方法1: 修改记忆系统密钥

编辑 `memory_system/app.py`:

```python
# 找到这行
MEMORY_KEY = "admin"

# 修改为你的密钥
MEMORY_KEY = "你的新密钥"
```

修改后重启:

```bash
pm2 restart memory-system
```

### 方法2: 修改OpenClaw的Basic Auth

编辑 `nginx/openclaw`:

```nginx
# 注释掉这两行即可禁用
# auth_basic "OpenClaw 登录";
# auth_basic_user_file /etc/nginx/.htpasswd;
```

然后重载Nginx:

```bash
sudo nginx -s reload
```

---

## 📋 常用命令

### 记忆系统

```bash
# 查看状态
pm2 status memory-system

# 查看日志
pm2 logs memory-system

# 重启
pm2 restart memory-system

# 停止
pm2 stop memory-system
```

### Nginx

```bash
# 测试配置
sudo nginx -t

# 重载
sudo nginx -s reload

# 重启
sudo systemctl restart nginx
```

### 手动同步对话

```bash
python3 scripts/sync_sessions.py
```

### 测试记忆召回

```bash
python3 scripts/recall_memory.py 关键词
```

---

## 🔧 访问地址

部署后访问:

- **OpenClaw**: `https://your-domain.com/` 或 `https://your-ip/`
- **记忆系统**: `https://your-domain.com/memory`
- **默认密钥**: `admin`

---

## 🐛 常见问题

### 1. 502错误

- 检查记忆系统是否运行: `pm2 status`
- 检查端口2323是否被占用: `ss -tlnp | grep 2323`

### 2. 无法登录

- 检查密钥是否正确: 默认是 `admin`
- 查看日志: `pm2 logs memory-system`

### 3. 搜索不到内容

- 运行同步: `python3 scripts/sync_sessions.py`
- 检查数据库: `sqlite3 memory_system/data/memory.db`

### 4. API无法访问

- 检查防火墙: `sudo ufw allow 2323`
- 检查Token是否过期

---

## 📡 API接口

### 查询记忆

```bash
curl -X POST http://localhost:2323/api/memory/query \
  -H "Content-Type: application/json" \
  -d '{"query": "关键词", "limit": 5}'
```

### 同步对话

```bash
curl -X POST http://localhost:2323/memory/api/sync \
  -H "Cookie: memory_token=你的token"
```

---

## 📅 更新日志

- 2026-03-17: 初始版本
  - 记忆系统基础功能
  - 问答自动保存
  - FTS5搜索
  - PM2进程守护

---

## 🤝 支持

有问题请提交 Issue: https://github.com/Vuay/open_claw/issues
