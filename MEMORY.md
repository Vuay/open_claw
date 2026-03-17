# MEMORY.md - 长期记忆

## 记忆系统 Web 端 (2026-03-17)

### 配置信息
- **访问地址**: https://115.191.17.111/memory
- **端口**: 2323
- **密钥**: miao669
- **认证方式**: 密钥（URL参数或Header）

### 技术实现
- Flask Web服务，独立于OpenClaw
- 禁用Basic Auth，独立认证
- 支持本地存储密钥（浏览器）
- 服务开机自启: memory-server

### 文件位置
- 服务脚本: `/root/.openclaw/workspace/memory_server.py`
- systemd服务: `/etc/systemd/system/memory-server.service`

## Clash 配置 (2026-03-16)

### 服务信息
- **服务名**: mihomo
- **HTTP端口**: 7890
- **WebUI**: http://115.191.17.111:9090
- **密钥**: 1lhPfP

### 订阅
| ID | URL |
|----|-----|
| 1 | https://821c4.no-mad-world.club/link/2zN7JF2dVyPkWS54?clash=3&extend=1 (主用) |
| 2 | https://skjk888.com/rss/cv1/kRAyrTM/C4kuf_ |
| 3 | https://eyu02.no-mad-world.club/link/Eg4Si8aAEfdAUevP?clash=3&extend=1 |

### 代理组
- 🔰 选择节点: 主选择器，包含自动选择组
- ⚡ 自动选择 (最低延迟): url-test类型，自动测速切换

### 常用命令
```bash
# 查看状态
systemctl status mihomo

# 重启
systemctl restart mihomo

# 查看日志
journalctl -u mihomo -f
```
