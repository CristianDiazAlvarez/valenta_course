"""
Forma principal de interactuar con los modelos de lenguaje de OpenAI.

Para crear una respuesta de ChatCompletion API, necesitamos pasarle un modelo y un historial de mensajes.
Este historial de mensajes es una lista de mensajes,
donde cada mensaje tiene un rol (system, user, assistant) y un contenido (content).

El role de system es el que se le da al modelo como instrucción de cómo debe responder.
El role de user es el que se le da al modelo para que entienda el mensaje del usuario.
El role de assistant es el que se completa con la respuesta del modelo.
"""

import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY")) # https://platform.openai.com/

history_chat = [{
            "role": "system",
            "content": "Te llamas PacoGPT, presentante como tal"
        }]

input_text=""
print("inciando chat")
print("#################")
while input_text != "exit":

    input_text = input("escribe algo: ")

    history_chat.append({
       "role": "user",
       "content": input_text
   })
    response = client.chat.completions.create(
    model="gpt-4o",
    messages=history_chat,
    max_tokens=100,
    temperature=0.2
    )
    history_chat.append({
       "role": "assistant",
       "content": response.choices[0].message.content
   })
    print("--------------------")
    print(response.choices[0].message.content)
print("#################")
print("fin chat")



