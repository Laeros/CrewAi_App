import os
from dotenv import load_dotenv
load_dotenv()

from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "Actúa como experto en historia."},
        {"role": "user", "content": "¿Quién fue Túpac Amaru II?"}
    ]
)

print(response.choices[0].message.content)
