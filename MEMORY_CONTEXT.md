# 记忆系统使用说明

## 自动召回
在回复用户之前，先调用记忆召回脚本查询相关历史对话。

## 调用方式
```bash
python3 /root/.openclaw/workspace/scripts/recall_memory.py [用户问题关键词]
```

## 示例
用户问: "我之前让你部署过什么？"
→ 调用: python3 recall_memory.py 部署
→ 获取相关记忆后融入回答
