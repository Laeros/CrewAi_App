import json
import os
import traceback
from flask import Blueprint, request, jsonify
from openai import OpenAI
from openai.types.chat import (
    ChatCompletionSystemMessageParam,
    ChatCompletionUserMessageParam
)
from app.models import Agent as AgentModel, Tool as ToolModel, ChatLog, db

api_bp = Blueprint('api', __name__, url_prefix='/api')

# ====== ENDPOINTS PARA AGENTES ======

@api_bp.route('/agents', methods=['POST', 'OPTIONS'])
def create_agent():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        agent_data = request.get_json()
        print(f"Datos recibidos para crear agente: {agent_data}")
        
        # Validación de datos requeridos
        required_fields = ['name', 'prompt', 'llm_provider', 'model', 'temperature', 'max_tokens']
        for field in required_fields:
            if field not in agent_data:
                return jsonify({'error': f'Campo requerido faltante: {field}'}), 400

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
        
        print(f"Agente creado exitosamente con ID: {agent.id}")
        return jsonify({
            "message": "Agente creado exitosamente", 
            "agent_id": agent.id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Error en create_agent: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({
            'error': 'Error interno del servidor',
            'message': str(e)
        }), 500

@api_bp.route('/agents', methods=['GET', 'OPTIONS'])
def list_agents():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
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
        
    except Exception as e:
        print(f"Error en list_agents: {str(e)}")
        return jsonify({'error': 'Error al listar agentes'}), 500

@api_bp.route('/agents/<int:agent_id>', methods=['PUT', 'OPTIONS'])
def update_agent(agent_id):
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
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
        
    except Exception as e:
        db.session.rollback()
        print(f"Error en update_agent: {str(e)}")
        return jsonify({'error': 'Error al actualizar agente'}), 500

@api_bp.route('/agents/<int:agent_id>', methods=['DELETE', 'OPTIONS'])
def delete_agent(agent_id):
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        agent = AgentModel.query.get_or_404(agent_id)
        db.session.delete(agent)
        db.session.commit()
        return jsonify({"message": "Agente eliminado correctamente"}), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Error en delete_agent: {str(e)}")
        return jsonify({'error': 'Error al eliminar agente'}), 500

# ====== ENDPOINTS PARA HERRAMIENTAS ======

@api_bp.route('/tools', methods=['POST', 'OPTIONS'])
def create_tool():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        print(f"Datos recibidos para crear tool: {data}")
        
        # Validación de datos
        if not data or 'name' not in data or 'description' not in data:
            return jsonify({'error': 'Faltan campos requeridos: name, description'}), 400
        
        tool_parameters = data.get('parameters', {})
        
        # Procesar parámetros
        if isinstance(tool_parameters, str):
            try:
                tool_parameters = json.loads(tool_parameters)
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON parameters: {e}")
                return jsonify({'error': 'Parámetros JSON inválidos'}), 400

        # Asegurar que los parámetros tengan la estructura correcta
        if "type" not in tool_parameters:
            tool_parameters = {
                "type": "object",
                "properties": tool_parameters,
                "required": list(tool_parameters.keys()) if tool_parameters else []
            }

        # Crear tool
        tool = ToolModel(
            name=data['name'],
            description=data['description'],
            parameters=tool_parameters
        )
        
        db.session.add(tool)
        db.session.commit()
        
        print(f"Tool creada exitosamente con ID: {tool.id}")
        return jsonify({
            "message": "Tool creada exitosamente", 
            "tool_id": tool.id,
            "tool": {
                "id": tool.id,
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.parameters
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Error en create_tool: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({
            'error': 'Error interno del servidor',
            'message': str(e)
        }), 500

@api_bp.route('/tools', methods=['GET', 'OPTIONS'])
def list_tools():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        tools = ToolModel.query.all()
        tool_list = [{
            "id": tool.id, 
            "name": tool.name,
            "description": tool.description,
            "parameters": tool.parameters
        } for tool in tools]
        return jsonify(tool_list), 200
        
    except Exception as e:
        print(f"Error en list_tools: {str(e)}")
        return jsonify({'error': 'Error al listar herramientas'}), 500

@api_bp.route('/tools/<int:tool_id>', methods=['PUT', 'OPTIONS'])
def update_tool(tool_id):
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        tool = ToolModel.query.get_or_404(tool_id)
        
        tool.name = data.get('name', tool.name)
        tool.description = data.get('description', tool.description)
        
        if 'parameters' in data:
            tool_parameters = data['parameters']
            if isinstance(tool_parameters, str):
                tool_parameters = json.loads(tool_parameters)
            tool.parameters = tool_parameters
        
        db.session.commit()
        return jsonify({"message": "Tool actualizada correctamente"}), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Error en update_tool: {str(e)}")
        return jsonify({'error': 'Error al actualizar herramienta'}), 500

@api_bp.route('/tools/<int:tool_id>', methods=['DELETE', 'OPTIONS'])
def delete_tool(tool_id):
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        tool = ToolModel.query.get_or_404(tool_id)
        db.session.delete(tool)
        db.session.commit()
        return jsonify({"message": "Tool eliminada correctamente"}), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Error en delete_tool: {str(e)}")
        return jsonify({'error': 'Error al eliminar herramienta'}), 500

# ====== ENDPOINTS PARA CHATS ======

@api_bp.route('/agents/<int:agent_id>/chats', methods=['GET', 'OPTIONS'])
def list_chats(agent_id):
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        chats = ChatLog.query.filter_by(agent_id=agent_id).all()
        chat_list = [{
            "id": chat.id,
            "message": chat.message,
            "role": getattr(chat, 'role', 'user'),
            "timestamp": chat.timestamp.isoformat() if chat.timestamp else None
        } for chat in chats]
        return jsonify(chat_list), 200
        
    except Exception as e:
        print(f"Error en list_chats: {str(e)}")
        return jsonify({'error': 'Error al listar chats'}), 500

@api_bp.route('/agents/<int:agent_id>/chats', methods=['DELETE', 'OPTIONS'])
def delete_chats(agent_id):
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        chats = ChatLog.query.filter_by(agent_id=agent_id).all()
        for chat in chats:
            db.session.delete(chat)
        db.session.commit()
        return jsonify({"message": "Chats eliminados correctamente"}), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Error en delete_chats: {str(e)}")
        return jsonify({'error': 'Error al eliminar chats'}), 500

# ====== ENDPOINT PARA CHAT CON AGENTE ======

@api_bp.route('/chat/<int:agent_id>', methods=['POST', 'OPTIONS'])
def chat_with_agent(agent_id):
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({'error': 'Mensaje requerido'}), 400
        
        agent_db = AgentModel.query.get_or_404(agent_id)
        
        # Configurar OpenAI
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return jsonify({'error': 'API key de OpenAI no configurada'}), 500
            
        client = OpenAI(api_key=api_key)

        # Preparar tools
        tools = []
        for tool in agent_db.tools:
            if tool.description and tool.parameters:
                tools.append({
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool.parameters
                    }
                })

        # Preparar mensajes
        messages = [
            {"role": "system", "content": agent_db.prompt},
            {"role": "user", "content": data["message"]}
        ]

        print(f"Enviando mensaje a OpenAI con {len(tools)} tools")

        # Primera llamada al modelo
        response = client.chat.completions.create(
            model=agent_db.model,
            messages=messages,
            tools=tools if tools else None,
            tool_choice="auto" if tools else None,
            temperature=agent_db.temperature,
            max_tokens=agent_db.max_tokens
        )

        assistant_message = response.choices[0].message
        tool_calls = assistant_message.tool_calls
        tool_messages = []

        if tool_calls:
            print(f"Procesando {len(tool_calls)} tool calls")
            
            for tool_call in tool_calls:
                tool_name = tool_call.function.name
                try:
                    tool_args = json.loads(tool_call.function.arguments)
                except Exception:
                    tool_args = {}

                # Simular ejecución de herramientas (aquí puedes implementar tu lógica real)
                if tool_name == "buscar_web":
                    result = f"Resultado simulado para búsqueda: {tool_args.get('query', '')}"
                elif tool_name == "Pensar":
                    result = f"Procesando pensamiento: {tool_args}"
                else:
                    result = f"[Simulación] Herramienta '{tool_name}' ejecutada con argumentos: {tool_args}"

                tool_messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result
                })

            # Añadir assistant message con tool_calls
            messages.append({
                "role": "assistant",
                "content": assistant_message.content,
                "tool_calls": [tc.model_dump() for tc in tool_calls]
            })
            messages.extend(tool_messages)

            # Segunda llamada al modelo (después de tools)
            final_response = client.chat.completions.create(
                model=agent_db.model,
                messages=messages,
                temperature=agent_db.temperature,
                max_tokens=agent_db.max_tokens
            )
            final_message = final_response.choices[0].message.content
        else:
            final_message = assistant_message.content

        # Guardar el log del chat
        log = ChatLog(
            agent_id=agent_id, 
            message=data["message"],
            role='user'
        )
        db.session.add(log)
        
        # Guardar también la respuesta del asistente
        assistant_log = ChatLog(
            agent_id=agent_id,
            message=final_message,
            role='assistant'
        )
        db.session.add(assistant_log)
        
        db.session.commit()
        
        return jsonify({"respuesta": final_message}), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Error en chat_with_agent: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({
            'error': 'Error en el chat',
            'message': str(e)
        }), 500

# ====== FUNCIONES AUXILIARES ======

def call_llm(agent, message):
    """Función auxiliar para llamadas a LLM"""
    try:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("API key de OpenAI no configurada")
            
        client = OpenAI(api_key=api_key)
        
        # Construir tools
        tools = []
        for tool in agent.tools:
            tools.append({
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.parameters
                }
            })
        
        # Mensajes tipados
        messages = [
            ChatCompletionSystemMessageParam(role="system", content=agent.prompt),
            ChatCompletionUserMessageParam(role="user", content=message)
        ]
        
        # Logs de depuración
        print("===== Llamada a OpenAI =====")
        print("Model:", agent.model)
        print("Messages:", messages)
        print("Tools:", len(tools))
        print("=============================")
        
        response = client.chat.completions.create(
            model=agent.model,
            messages=messages,
            tools=tools if tools else None,
            temperature=agent.temperature,
            max_tokens=agent.max_tokens
        )
        
        print("===== Respuesta de OpenAI =====")
        print("Response:", response.choices[0].message.content)
        print("================================")
        
        if response.choices and response.choices[0].message:
            return response.choices[0].message.content
        else:
            return "Respuesta vacía o sin contenido."
            
    except Exception as e:
        print(f"Error en call_llm: {str(e)}")
        return f"Error al procesar con LLM: {str(e)}"

def create_agent_response(agent, message):
    """Función auxiliar para crear respuesta simple del agente"""
    try:
        if agent.provider.lower() == 'openai':
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                return "Error: API key de OpenAI no configurada"
                
            client = OpenAI(api_key=api_key)
            
            messages = [
                ChatCompletionSystemMessageParam(role="system", content=agent.prompt),
                ChatCompletionUserMessageParam(role="user", content=message)
            ]
            
            completion = client.chat.completions.create(
                model=agent.model,
                messages=messages,
                temperature=agent.temperature,
                max_tokens=agent.max_tokens
            )
            return completion.choices[0].message.content
        else:
            return "LLM provider no soportado"
            
    except Exception as e:
        print(f"Error en create_agent_response: {str(e)}")
        return f"Error al generar respuesta: {str(e)}"
