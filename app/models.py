from sqlalchemy.dialects.postgresql import JSONB

from . import db
from datetime import datetime, timezone

AgentTool = db.Table('agent_tool',
    db.Column('agent_id', db.Integer, db.ForeignKey('agent.id')),
    db.Column('tool_id', db.Integer, db.ForeignKey('tool.id'))
)

class Agent(db.Model):
    __tablename__ = 'agent'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    prompt = db.Column(db.Text, nullable=False)
    provider = db.Column(db.String(50), nullable=False)
    model = db.Column(db.String(100), nullable=False)
    temperature = db.Column(db.Float, nullable=False, default=0.1)
    max_tokens = db.Column(db.Integer, nullable=False, default=50)

    tools = db.relationship('Tool', secondary=agent_tool, backref='agents')

class Tool(db.Model):
    __tablename__ = 'tool'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.Text, nullable=False)
    parameters = db.Column(JSONB, nullable=False)  # ⚠️ Guardamos los parámetros como JSON

class AgentTool(db.Model):
    __tablename__ = 'agent_tool'
    id = db.Column(db.Integer, primary_key=True)
    agent_id = db.Column(db.Integer, db.ForeignKey('agent.id'))
    tool_id = db.Column(db.Integer, db.ForeignKey('tool.id'))

class ChatLog(db.Model):
    __tablename__ = 'chat_log'
    id = db.Column(db.Integer, primary_key=True)
    agent_id = db.Column(db.Integer, db.ForeignKey('agent.id'))
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))