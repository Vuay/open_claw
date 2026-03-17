#!/bin/bash
# 监控内存使用，超过80%告警
MEM_USAGE=$(free | grep Mem | awk '{print ($3/$2) * 100}')
if [ "$MEM_USAGE" -gt 80 ]; then
 echo "$(date): WARNING - Memory usage: $MEM_USAGE%" >> /var/log/memory_system.log
 sync && echo 3 > /proc/sys/vm/drop_caches 2>/dev/null
fi

# 监控存储
DISK_USAGE=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -gt 85 ]; then
 echo "$(date): WARNING - Disk usage: $DISK_USAGE%" >> /var/log/memory_system.log
fi
