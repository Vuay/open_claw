#!/bin/bash
cd /root/.openclaw/workspace

# 只备份更改的文件
git add -A

# 检查是否有变化
if git diff --cached --quiet; then
 echo "$(date): No changes to commit"
 exit 0
fi

# 增量提交
git commit -m "Incremental: $(date +'%Y-%m-%d %H:%M')"

# 保持最近的50个提交
git prune
git gc --prune=now --aggressive 2>/dev/null
