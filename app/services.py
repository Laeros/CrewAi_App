from openai import OpenAI
from openai.types.chat import (
    ChatCompletionSystemMessageParam,
    ChatCompletionUserMessageParam
)
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def call_llm(agent, message):
    # Construir tools reales
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

    # Usar las clases tipadas correctas
    messages = [
        ChatCompletionSystemMessageParam(role="system", content=agent.prompt),
        ChatCompletionUserMessageParam(role="user", content=message)
    ]

    # Logs de depuración
    print("===== Llamada a OpenAI =====")
    print("Model:", agent.model)
    print("Messages:", messages)
    print("Tools:", tools)
    print("=============================")

    response = client.chat.completions.create(
        model=agent.model,
        messages=messages,
        tools=tools if tools else None
    )

    print("===== Respuesta bruta de OpenAI =====")
    print(response)
    print("=============================")

    # Verifica que la respuesta contenga un mensaje válido
    if response.choices and response.choices[0].message:
        return response.choices[0].message.content
    else:
        return "Respuesta vacía o sin contenido."

def create_agent_response(agent, message):
    if agent.provider.lower() == 'openai':
        messages = [
            ChatCompletionSystemMessageParam(role="system", content=agent.prompt),
            ChatCompletionUserMessageParam(role="user", content=message)
        ]

        completion = client.chat.completions.create(
            model="gpt-4.1-nano-2025-04-14",
            messages=messages,
            temperature=agent.temperature,
            max_tokens=agent.max_tokens
        )

        return completion.choices[0].message.content
    else:
        return "LLM provider no soportado"