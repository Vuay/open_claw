#!/bin/bash
# 每天执行的任务（合并）

# 1. 记忆分层同步
python3 /root/.openclaw/memory_system/services/layer_service.py

# 2. 增量Git备份
/root/.openclaw/workspace/incremental_backup.sh

echo "$(date): Daily tasks completed"
