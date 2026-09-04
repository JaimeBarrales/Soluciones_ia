# Outfitly

##  Descripción del Proyecto

**Outfitly** aborda la problemática que enfrentan las tiendas de ropa tanto físicas como online, donde los clientes suelen tener dificultades para visualizar combinaciones de prendas o verificar su disponibilidad real. Esto genera ventas perdidas y una alta tasa de devoluciones.

A través de un agente de Inteligencia Artificial que integra **LLMs** y técnicas de **RAG**, Outfitly se conecta directamente al inventario de la tienda para ofrecer:
* **Recomendaciones personalizadas** de estilo según la ocasión.
* **Respuestas basadas en stock real**, evitando sugerencias de productos agotados o inexistentes.
* **Asesoría de tallas y disponibilidad** inmediata mediante un chatbot interactivo en **Streamlit**.

* ## 🛠️ Arquitectura y Tecnologías

* **LLM & RAG Pipeline:** Generación de respuestas fundamentadas en contexto real.
* **Vector Database:** [ChromaDB](https://www.trychroma.com/) para búsqueda por similitud semántica.
* **Base de Datos NoSQL:** [MongoDB](https://www.mongodb.com/) para gestión de historial y logs.
* **Frontend / UI:** [Streamlit](https://streamlit.io/) para una interfaz conversacional fluida.
* **Contenerización:** Docker.

##  Estructura del Repositorio

```text
SolucionesIA/
├── data/                  # Catálogo de productos y base vectorial (ChromaDB)
├── eval/                  # Datasets y scripts de evaluación del modelo
├── promts/                # Prompts del sistema para el LLM
└── src/                   # Código fuente principal
    ├── generate/          # Módulo de generación de respuestas
    ├── ingesta/           # Pipeline de ingesta de datos
    ├── retrievals/        # Búsqueda e indexación vectorial
    └── utils/             # App Streamlit, configuración de base de datos y utilidades
