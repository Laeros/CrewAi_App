import json

from flask import Blueprint, request, jsonify
from app.models import Agent as AgentModel, Tool as ToolModel, ChatLog, db, Tool
from crewai import Agent, Task, Crew
import os


api_bp = Blueprint('api', __name__, url_prefix='/api')

# Endpoint para crear un agente
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

    # Convierte a JSON real si viene como string
    tool_parameters = data.get('parameters')
    if isinstance(tool_parameters, str):
        tool_parameters = json.loads(tool_parameters)

    tool = ToolModel(
        name=data['name'],
        description=data['description'],
        parameters=tool_parameters
    )
    db.session.add(tool)
    db.session.commit()
    return jsonify({"message": "Tool creada exitosamente", "tool_id": tool.id}), 201

# Endpoint para listar todos los agentes
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

# Endpoint para actualizar un agente
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

# Endpoint para eliminar un agente
@api_bp.route('/agents/<int:agent_id>', methods=['DELETE'])
def delete_agent(agent_id):
    agent = AgentModel.query.get_or_404(agent_id)
    db.session.delete(agent)
    db.session.commit()
    return jsonify({"message": "Agente eliminado correctamente"}), 200

# Endpoint para listar todas las herramientas
@api_bp.route('/tools', methods=['GET'])
def list_tools():
    tools = ToolModel.query.all()
    tool_list = [{"id": tool.id, "name": tool.name} for tool in tools]
    return jsonify(tool_list), 200

# Endpoint para actualizar una herramienta
import json

@api_bp.route('/tools/<int:tool_id>', methods=['PUT'])
def update_tool(tool_id):
    data = request.get_json()
    tool = ToolModel.query.get_or_404(tool_id)

    # Actualiza los campos si están presentes en el JSON de la petición
    tool.name = data.get('name', tool.name)
    tool.description = data.get('description', tool.description)

    # Convierte a objeto JSON real si viene como string
    tool_parameters = data.get('parameters')
    if tool_parameters:
        if isinstance(tool_parameters, str):
            tool_parameters = json.loads(tool_parameters)
        tool.parameters = tool_parameters

    db.session.commit()
    return jsonify({"message": "Tool actualizada correctamente"}), 200


# Endpoint para eliminar una herramienta
@api_bp.route('/tools/<int:tool_id>', methods=['DELETE'])
def delete_tool(tool_id):
    tool = ToolModel.query.get_or_404(tool_id)
    db.session.delete(tool)
    db.session.commit()
    return jsonify({"message": "Tool eliminada correctamente"}), 200

# Endpoint para listar los chats de un agente
@api_bp.route('/agents/<int:agent_id>/chats', methods=['GET'])
def list_chats(agent_id):
    chats = ChatLog.query.filter_by(agent_id=agent_id).all()
    chat_list = [{
        "id": chat.id,
        "message": chat.message,
        "timestamp": chat.timestamp.isoformat() if chat.timestamp else None
    } for chat in chats]
    return jsonify(chat_list), 200

# Endpoint para eliminar los chats de un agente
@api_bp.route('/agents/<int:agent_id>/chats', methods=['DELETE'])
def delete_chats(agent_id):
    chats = ChatLog.query.filter_by(agent_id=agent_id).all()
    for chat in chats:
        db.session.delete(chat)
    db.session.commit()
    return jsonify({"message": "Chats eliminados correctamente"}), 200

# Endpoint para interactuar con un agente
@api_bp.route('/chat/<int:agent_id>', methods=['POST'])
def chat_with_agent(agent_id):
    data = request.get_json()
    agent_db = AgentModel.query.get_or_404(agent_id)

    os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
    llm_model = agent_db.model

    # Configuración de herramientas solo si existen y están bien definidas
    tools = []
    for tool in agent_db.tools:
        if tool.description and tool.parameters:
            tools.append({
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.parameters  # Debe ser un dict bien formado
                }
            })

    # Genera el Crew (sin error de tools vacías)
    if tools:
        crew = Crew(
            agents=[
                Agent(
                    role="user",
                    goal="Responder usando el prompt configurado y las herramientas",
                    backstory=agent_db.prompt,
                    verbose=True,
                    allow_delegation=True,
                    llm=llm_model
                )
            ],
            tasks=[
                Task(
                    description=data['message'],
                    expected_output="Una respuesta breve y clara del agente.",
                    agent=None  # No es necesario, ya está en la lista de agentes
                )
            ],
            tools=tools
        )
    else:
        crew = Crew(
            agents=[
                Agent(
                    role="user",
                    goal="Responder usando el prompt configurado",
                    backstory=agent_db.prompt,
                    verbose=True,
                    allow_delegation=True,
                    llm=llm_model
                )
            ],
            tasks=[
                Task(
                    description=data['message'],
                    expected_output="Una respuesta breve y clara del agente.",
                    agent=None
                )
            ]
        )

    output = crew.kickoff()

    # Guarda el log del chat
    log = ChatLog(agent_id=agent_id, message=data['message'])
    db.session.add(log)
    db.session.commit()

    return jsonify({"respuesta": str(output)}), 200

