# 🦞 OpenClaw 记忆系统部署配置

本仓库包含 OpenClaw 记忆系统的完整部署配置。

## 📦 包含内容

| 目录 | 说明 |
|------|------|
| `.openclaw/` | OpenClaw配置 |
| `memory_system/` | Flask记忆系统Web应用 |
| `nginx/` | Nginx反向代理配置 |
| `scripts/` | 同步和召回脚本 |

## 🚀 部署步骤

### 1. 安装依赖
```bash
pip3 install flask flask-sqlalchemy flask-cors requests
```

### 2. 配置Nginx
```bash
sudo cp nginx/openclaw /etc/nginx/sites-available/
sudo ln -sf /etc/nginx/sites-available/openclaw /etc/nginx/sites-enabled/
sudo nginx -t && sudo nginx -s reload
```

### 3. 启动记忆系统
```bash
cd memory_system
pm2 start app.py --name memory-system
pm2 save
```

## 🔧 访问地址

- OpenClaw: `https://your-domain.com/`
- 记忆系统: `https://your-domain.com/memory`
- 密钥: `miao669`

## 📝 API

- `POST /api/memory/query` - 查询记忆

## 📅 更新日志

- 2026-03-17: 初始版本
