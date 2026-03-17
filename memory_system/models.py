#!/usr/bin/env python3
"""
记忆系统 - 数据模型 (SQLAlchemy)
"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Conversation(db.Model):
    """对话记录"""
    id = db.Column(db.String(64), primary_key=True)
    title = db.Column(db.String(256))
    summary = db.Column(db.Text)
    message = db.Column(db.Text)  # 用户消息
    time = db.Column(db.String(32))
    messages_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'summary': self.summary,
            'message': self.message,
            'time': self.time,
            'messages_count': self.messages_count,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Memory(db.Model):
    """记忆文件"""
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(256), unique=True)
    content = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'content': self.content,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Token(db.Model):
    """JWT Token存储"""
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(128), unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)
    
    def is_valid(self):
        return datetime.utcnow() < self.expires_at
