"""
app.py
Interfaz de chat con Streamlit para Outfitly.
Streamlit trae st.chat_message / st.chat_input listos, así que no hay
que armar la UI de chat a mano — solo conectarla al pipeline de RAG.

Correr con:
    streamlit run src/utils/app.py
"""

import streamlit as st

# Ajusta estos imports según cómo terminen llamándose tus módulos reales
from src.retrievals.retrievals import buscar_prendas
from src.generate.generate import generar_respuesta


st.set_page_config(page_title="Outfitly", page_icon="👕")
st.title("Outfitly")
st.caption("Tu asistente de outfits — solo recomienda lo que hay en stock")

# --- Estado de la conversación ---
if "mensajes" not in st.session_state:
    st.session_state.mensajes = [
        {"role": "assistant", "content": "Hola, soy Outfitly 👋 Cuéntame qué buscas (ocasión, estilo, talla) y te armo un outfit con lo que tenemos disponible."}
    ]

# --- Pintar historial ---
for msg in st.session_state.mensajes:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- Input del usuario ---
query = st.chat_input("Ej: necesito un outfit casual para una entrevista, talla M")

if query:
    # 1. Mostrar mensaje del usuario
    st.session_state.mensajes.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)

    # 2. Retrieval: traer solo prendas relevantes y en stock
    with st.spinner("Buscando en el catálogo..."):
        prendas_relevantes = buscar_prendas(query, top_k=6)

    # 3. Generation: el LLM arma la recomendación SOLO con esas prendas
    with st.chat_message("assistant"):
        with st.spinner("Armando tu outfit..."):
            respuesta = generar_respuesta(
                query=query,
                contexto=prendas_relevantes,
                historial=st.session_state.mensajes,
            )
        st.markdown(respuesta)

        # Mostrar las prendas usadas como tarjetas, para que el usuario
        # vea que son productos reales del catálogo (transparencia)
        if prendas_relevantes:
            with st.expander("Ver prendas encontradas"):
                for p in prendas_relevantes:
                    meta = p.get("metadata", p)  # depende del formato que devuelva tu retrieval
                    st.markdown(
                        f"**{meta.get('nombre', 'Producto')}** — "
                        f"{meta.get('color', '')}, talla {meta.get('talla', '')} — "
                        f"${meta.get('precio', 0):.0f} — "
                        f"Stock: {meta.get('stock', 0)}"
                    )

    # 4. Guardar respuesta en el historial
    st.session_state.mensajes.append({"role": "assistant", "content": respuesta})