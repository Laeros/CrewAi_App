from flask import Blueprint, request, jsonify
from app.models import Agent as AgentModel, Tool as ToolModel, ChatLog, db, Tool
from crewai import Agent, Task, Crew
import os

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/agents', methods=['POST'])
def create_agent():
    agent_data = request.get_json()
    name = agent_data['name']
    prompt = agent_data['prompt']
    provider = agent_data['llm_provider']
    model = agent_data['model']
    temperature = agent_data['temperature']
    max_tokens = agent_data['max_tokens']
    tools = agent_data.get('tools', [])

    agent = AgentModel(
        name=name,
        prompt=prompt,
        provider=provider,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens
    )

    if tools:
        associated_tools = ToolModel.query.filter(ToolModel.name.in_(tools)).all()
        agent.tools.extend(associated_tools)

    db.session.add(agent)
    db.session.commit()

    return jsonify({"message": "Agente creado exitosamente", "agent_id": agent.id}), 201

@api_bp.route('/tools', methods=['POST'])
def create_tool():
    data = request.get_json()
    tool = ToolModel(name=data['name'])
    db.session.add(tool)
    db.session.commit()
    return jsonify({"message": "Tool creada exitosamente", "tool_id": tool.id}), 201

@api_bp.route('/agents/<int:agent_id>/chats', methods=['GET'])
def list_chats(agent_id):
    chats = ChatLog.query.filter_by(agent_id=agent_id).all()
    chat_list = [{
        "id": chat.id,
        "message": chat.message,
        "timestamp": chat.timestamp.isoformat()
    } for chat in chats]
    return jsonify(chat_list), 200

@api_bp.route('/agents/<int:agent_id>/chats', methods=['DELETE'])
def delete_chats(agent_id):
    chats = ChatLog.query.filter_by(agent_id=agent_id).all()
    for chat in chats:
        db.session.delete(chat)
    db.session.commit()
    return jsonify({"message": "Chats eliminados correctamente"}), 200

@api_bp.route('/agents', methods=['GET'])
def list_agents():
    agents = AgentModel.query.all()
    agent_list = [{
        "id": agent.id,
        "name": agent.name,
        "prompt": agent.prompt,
        "provider": agent.provider,
        "model": agent.model,
        "temperature": agent.temperature,
        "max_tokens": agent.max_tokens,
        "tools": [tool.name for tool in agent.tools]
    } for agent in agents]
    return jsonify(agent_list), 200

@api_bp.route('/agents/<int:agent_id>', methods=['PUT'])
def update_agent(agent_id):
    data = request.get_json()
    agent = AgentModel.query.get_or_404(agent_id)
    agent.name = data.get('name', agent.name)
    agent.prompt = data.get('prompt', agent.prompt)
    agent.provider = data.get('llm_provider', agent.provider)
    agent.model = data.get('model', agent.model)
    agent.temperature = data.get('temperature', agent.temperature)
    agent.max_tokens = data.get('max_tokens', agent.max_tokens)

    if 'tools' in data:
        tools = ToolModel.query.filter(ToolModel.name.in_(data['tools'])).all()
        agent.tools = tools

    db.session.commit()
    return jsonify({"message": "Agente actualizado correctamente"}), 200

@api_bp.route('/agents/<int:agent_id>', methods=['DELETE'])
def delete_agent(agent_id):
    agent = AgentModel.query.get_or_404(agent_id)
    db.session.delete(agent)
    db.session.commit()
    return jsonify({"message": "Agente eliminado correctamente"}), 200

@api_bp.route('/tools', methods=['GET'])
def list_tools():
    tools = ToolModel.query.all()
    tool_list = [{"id": tool.id, "name": tool.name} for tool in tools]
    return jsonify(tool_list), 200

@api_bp.route('/tools/<int:tool_id>', methods=['PUT'])
def update_tool(tool_id):
    data = request.get_json()
    tool = ToolModel.query.get_or_404(tool_id)
    tool.name = data.get('name', tool.name)
    db.session.commit()
    return jsonify({"message": "Tool actualizada correctamente"}), 200

@api_bp.route('/tools/<int:tool_id>', methods=['DELETE'])
def delete_tool(tool_id):
    tool = ToolModel.query.get_or_404(tool_id)
    db.session.delete(tool)
    db.session.commit()
    return jsonify({"message": "Tool eliminada correctamente"}), 200

@api_bp.route('/chat/<int:agent_id>', methods=['POST'])
def chat_with_agent(agent_id):
    data = request.get_json()
    agent_db = AgentModel.query.get_or_404(agent_id)

    os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
    llm_model = agent_db.model

    crew_agent = Agent(
        role="user",
        goal="Responder según el prompt configurado",
        backstory=agent_db.prompt,
        verbose=True,
        allow_delegation=False,
        llm=llm_model
    )

    task = Task(
        description=data['message'],
        expected_output="Una respuesta corta del agente.",
        agent=crew_agent
    )

    crew = Crew(agents=[crew_agent], tasks=[task])
    output = crew.kickoff()

    log = ChatLog(agent_id=agent_id, message=data['message'])
    db.session.add(log)
    db.session.commit()

    return jsonify({"respuesta": str(output)}), 200