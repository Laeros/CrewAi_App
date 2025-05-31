from crewai import Agent
from openai import OpenAI
import os
import google.generativeai as genai

import requests


client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def create_agent_response(agent, message):
    if agent.provider.lower() == 'openai':
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": agent.prompt}, {"role": "user", "content": message}],
            temperature=agent.temperature,
            max_tokens=agent.max_tokens
        )
        return completion.choices[0].message.content
    elif agent.provider.lower() == 'google':
        genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
        model = genai.GenerativeModel("gemini-pro")
        result = model.generate_content(agent.prompt + "\n" + message)
        return result.text
    else:
        return "LLM provider no soportado"


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

    messages = [
        {"role": "system", "content": agent.prompt},
        {"role": "user", "content": message}
    ]

    response = client.chat.completions.create(
        model=agent.model,
        messages=messages,
        tools=tools if tools else None
    )

    return response.choices[0].message.content