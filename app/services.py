from openai import OpenAI
import os
import google.generativeai as genai

import requests

def create_agent_response(agent, message):
    if agent.provider.lower() == 'openai':
        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
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


import requests

def buscar_web(query: str) -> str:
    """
    Realiza una búsqueda web usando Bing o DuckDuckGo y devuelve un resumen.
    """
    # Ejemplo con DuckDuckGo Instant Answer API
    url = f"https://api.duckduckgo.com/?q={query}&format=json"
    response = requests.get(url)
    data = response.json()

    abstract = data.get("AbstractText", "")
    if abstract:
        return abstract
    else:
        return f"No se encontraron resultados para '{query}'."
