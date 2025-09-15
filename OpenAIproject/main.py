# app.py
# Chat multimodal básico con Streamlit + OpenAI (texto e imágenes)
# Ejecuta: streamlit run app.py

import os
import io
import base64
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

# -------------------------------
# Configuración inicial
# -------------------------------
load_dotenv()

st.set_page_config(page_title="Chat Multimodal GPT-4o", page_icon="💬", layout="centered")

API_KEY = os.getenv("OPENAI_API_KEY", "")

if not API_KEY:
    st.error("No se encontró OPENAI_API_KEY. Define la variable de entorno o usa .streamlit/secrets.toml.")
    st.stop()

client = OpenAI(api_key=API_KEY)

# -------------------------------
# Sidebar de controles
# -------------------------------
st.sidebar.title("⚙️ Configuración")
model = st.sidebar.selectbox("Modelo", ["gpt-4o"], index=0)
temperature = st.sidebar.slider("Creatividad (temperature)", 0.0, 1.0, 0.2, 0.1)
max_tokens = st.sidebar.slider("Límites de respuesta (max_tokens)", 64, 2048, 512, 64)

default_system = (
    "Eres un asistente útil, técnico y claro. "
    "Si el usuario adjunta imágenes, analízalas y referencia visualmente lo que observes."
)
system_prompt = st.sidebar.text_area("System prompt", value=default_system, height=120)

if st.sidebar.button("🗑️ Borrar conversación"):
    st.session_state.clear()
    st.rerun()

# -------------------------------
# Estado de la app
# -------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": system_prompt}
    ]
if "display_messages" not in st.session_state:
    # Para el render amigable en la UI (sin el system dentro del timeline)
    st.session_state.display_messages = []

# Si el system cambia, lo actualizamos en el historial (primer mensaje)
if st.session_state.messages and st.session_state.messages[0]["role"] == "system":
    st.session_state.messages[0]["content"] = system_prompt

# -------------------------------
# Header
# -------------------------------
st.title("💬 Chat multimodal con GPT-4o")
st.caption("Escribe un mensaje, adjunta imágenes y envía. El modelo responderá combinando texto e imagen.")

# -------------------------------
# Zona de subida de imágenes
# -------------------------------
uploaded_files = st.file_uploader(
    "Adjunta una o varias imágenes (PNG/JPG/JPEG, opcional)",
    type=["png", "jpg", "jpeg"],
    accept_multiple_files=True,
    help="Las imágenes se envían codificadas en base64 dentro del mensaje del usuario."
)

# Mostrar miniaturas y convertir a base64
def encode_image_to_base64(file) -> str:
    bytes_data = file.read()
    b64 = base64.b64encode(bytes_data).decode("utf-8")
    # devolvemos el puntero del buffer a 0 por si se vuelve a leer
    file.seek(0)
    return b64

image_blobs = []
if uploaded_files:
    st.write("**Imágenes cargadas:**")
    cols = st.columns(min(3, len(uploaded_files)))
    for idx, uf in enumerate(uploaded_files):
        with cols[idx % 3]:
            st.image(uf, use_container_width=True)
        try:
            b64 = encode_image_to_base64(uf)
            mime = "image/png" if uf.type in ("image/png",) else "image/jpeg"
            image_blobs.append((b64, mime))
        except Exception as e:
            st.warning(f"No se pudo procesar {uf.name}: {e}")

# -------------------------------
# Render del historial
# -------------------------------
for msg in st.session_state.display_messages:
    with st.chat_message("assistant" if msg["role"] == "assistant" else "user"):
        # texto
        if isinstance(msg["content"], str):
            st.markdown(msg["content"])
        else:
            # contenido multimodal renderizado (texto + imágenes)
            text_chunks = []
            images_to_render = []
            for part in msg["content"]:
                if isinstance(part, dict) and part.get("type") == "text":
                    text_chunks.append(part.get("text", ""))
                elif isinstance(part, dict) and part.get("type") == "image_url":
                    images_to_render.append(part["image_url"]["url"])
            if text_chunks:
                st.markdown("\n\n".join(text_chunks))
            for url in images_to_render:
                # Render de data URLs
                try:
                    header, b64data = url.split(",", 1)
                    st.image(io.BytesIO(base64.b64decode(b64data)))
                except Exception:
                    st.markdown(f"Imagen: {url}")

# -------------------------------
# Entrada de chat
# -------------------------------
user_text = st.chat_input("Escribe tu mensaje…")

def build_user_content(text: str, images: list[tuple[str, str]]):
    """
    Genera el content del mensaje de usuario en formato multimodal:
    - Si hay solo texto: string
    - Si hay imágenes: lista con {"type":"text"} + {"type":"image_url", ...}
    """
    if not images:
        return text.strip() if text else ""
    # multimodal: texto + imágenes
    content = []
    if text and text.strip():
        content.append({"type": "text", "text": text.strip()})
    for b64, mime in images:
        content.append({
            "type": "image_url",
            "image_url": {"url": f"data:{mime};base64,{b64}"}
        })
    return content

if user_text is not None:
    # Construimos el mensaje de usuario (multimodal si hay imágenes)
    user_content = build_user_content(user_text, image_blobs)

    # Guardamos en historial para la UI
    st.session_state.display_messages.append({"role": "user", "content": user_content})

    # Guardamos en historial para la API (incluye el system al inicio)
    st.session_state.messages.append({"role": "user", "content": user_content})

    # -------------------------------
    # Llamada a OpenAI
    # -------------------------------
    with st.chat_message("assistant"):
        with st.spinner("Pensando…"):
            try:
                # Nota: usamos Chat Completions por consistencia con tus scripts.
                resp = client.chat.completions.create(
                    model=model,
                    messages=st.session_state.messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                assistant_msg = resp.choices[0].message

                # Render inmediato en UI
                if isinstance(assistant_msg.content, str):
                    st.markdown(assistant_msg.content)
                else:
                    # En la API moderna, content suele ser string; este bloque es
                    # por si en el futuro hay partes multimodales en la respuesta.
                    text_chunks = []
                    images_to_render = []
                    for part in assistant_msg.content:
                        if isinstance(part, dict) and part.get("type") == "text":
                            text_chunks.append(part.get("text", ""))
                        elif isinstance(part, dict) and part.get("type") == "image_url":
                            images_to_render.append(part["image_url"]["url"])
                    if text_chunks:
                        st.markdown("\n\n".join(text_chunks))
                    for url in images_to_render:
                        try:
                            header, b64data = url.split(",", 1)
                            st.image(io.BytesIO(base64.b64decode(b64data)))
                        except Exception:
                            st.markdown(f"Imagen: {url}")

                # Añadir al historial (UI + API)
                st.session_state.display_messages.append({
                    "role": "assistant",
                    "content": assistant_msg.content
                })
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": assistant_msg.content
                })

            except Exception as e:
                st.error(f"Error en la llamada a OpenAI: {e}")


## promt de ejemplo para extracción en formato json

# Estructurame lo que se ve en este formato json:
# {"tienda": "nombre de la tienda", "posicion": "posicion de la tienda en la imagen"}

# Cual es el nombre de la tienda, y la posición de la misma, ocn las opciones de: arriba-izquierda, abajo-izquierda, arriba-derecha, abajo-derecha, centro.


# Si no encuentras ninguna tienda responde : {}