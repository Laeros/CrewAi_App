from app import db
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime

class Agent(db.Model):
    __tablename__ = 'agent'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    prompt = db.Column(db.Text, nullable=False)
    provider = db.Column(db.String, nullable=False)
    model = db.Column(db.String, nullable=False)
    temperature = db.Column(db.Float, nullable=False, default=0.1)
    max_tokens = db.Column(db.Integer, nullable=False, default=50)

    # Relaciones
    tools = db.relationship('Tool', secondary='agent_tool', backref='agents')
    chat_logs = db.relationship('ChatLog', backref='agent', cascade='all, delete-orphan')  # <-- clave

class Tool(db.Model):
    __tablename__ = 'tool'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=False)
    parameters = db.Column(db.JSON, nullable=False)

class AgentTool(db.Model):
    __tablename__ = 'agent_tool'
    id = db.Column(db.Integer, primary_key=True)
    agent_id = db.Column(db.Integer, db.ForeignKey('agent.id', ondelete='CASCADE'))
    tool_id = db.Column(db.Integer, db.ForeignKey('tool.id', ondelete='CASCADE'))

class ChatLog(db.Model):
    __tablename__ = 'chat_log'
    id = db.Column(db.Integer, primary_key=True)
    agent_id = db.Column(db.Integer, db.ForeignKey('agent.id', ondelete='CASCADE'))
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
