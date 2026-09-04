"""
retrievals.py
Búsqueda semántica sobre el catálogo vectorizado.
Usa Chroma (persistente en disco) porque es lo más simple de levantar
para un proyecto de curso, sin depender de un servicio externo.

Requiere haber corrido antes create_vector_index.py, que debería dejar
la colección persistida en la misma ruta CHROMA_PATH que se usa acá.
"""

import chromadb
from chromadb.utils import embedding_functions
from typing import List, Dict

CHROMA_PATH = "data/chroma_db"
COLLECTION_NAME = "catalogo_outfitly"

# Mismo modelo de embeddings que debe usarse en create_vector_index.py
# (si cambian el modelo en uno, hay que cambiarlo en el otro también)
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

_client = chromadb.PersistentClient(path=CHROMA_PATH)
_embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name=EMBEDDING_MODEL
)


def _get_collection():
    return _client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=_embedding_fn,
    )


def buscar_prendas(query: str, top_k: int = 6, filtro_categoria: str = None) -> List[Dict]:
    """
    Busca las prendas más relevantes para el query del usuario.

    Args:
        query: consulta en lenguaje natural del cliente
        top_k: cuántos resultados devolver
        filtro_categoria: opcional, ej. "Poleras", para acotar la búsqueda

    Returns:
        Lista de dicts: {id, texto, metadata, score}
        metadata trae: nombre, categoria, color, talla, precio, stock
    """
    coleccion = _get_collection()

    where = {"categoria": filtro_categoria} if filtro_categoria else None

    resultados = coleccion.query(
        query_texts=[query],
        n_results=top_k,
        where=where,
    )

    prendas = []
    ids = resultados.get("ids", [[]])[0]
    documentos = resultados.get("documents", [[]])[0]
    metadatas = resultados.get("metadatas", [[]])[0]
    distancias = resultados.get("distances", [[]])[0]

    for id_, texto, metadata, distancia in zip(ids, documentos, metadatas, distancias):
        # Doble chequeo de stock: aunque ya se filtró en la ingesta,
        # nunca está de más asegurarse antes de pasarle esto al LLM
        if metadata.get("stock", 0) <= 0:
            continue
        prendas.append({
            "id": id_,
            "texto": texto,
            "metadata": metadata,
            "score": 1 - distancia,  # similitud aproximada (mientras más alto, mejor)
        })

    return prendas


if __name__ == "__main__":
    # Prueba rápida desde consola
    resultados = buscar_prendas("outfit casual para una entrevista de trabajo, talla M")
    for r in resultados:
        print(f"{r['metadata']['nombre']} | score={r['score']:.2f} | stock={r['metadata']['stock']}")