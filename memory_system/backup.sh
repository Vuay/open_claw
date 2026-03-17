#!/bin/bash
BACKUP_DIR="/root/.openclaw/memory_system/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# 备份数据库
cp /root/.openclaw/memory_system/data/memory.db "$BACKUP_DIR/memory_$DATE.db" 2>/dev/null

# 备份对话文件
cp /root/.openclaw/workspace/memory/conversations.json "$BACKUP_DIR/conversations_$DATE.json" 2>/dev/null

# 清理7天前的备份
find $BACKUP_DIR -name "*.db" -mtime +7 -delete 2>/dev/null
find $BACKUP_DIR -name "*.json" -mtime +7 -delete 2>/dev/null

echo "[$(date)] 备份完成"
