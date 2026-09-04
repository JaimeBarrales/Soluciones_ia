"""
create_vector_index.py
Toma los documentos generados por ingesta.py (data/documentos_procesados.json)
y los indexa en Chroma para que retrievals.py pueda buscarlos.

IMPORTANTE: CHROMA_PATH, COLLECTION_NAME y EMBEDDING_MODEL deben ser
idénticos a los que usa retrievals.py, o vas a estar consultando una
colección distinta a la que llenaste acá.

Correr con:
    python src/utils/create_vector_index.py
"""

import json
import chromadb
from chromadb.utils import embedding_functions
from pathlib import Path

CHROMA_PATH = "data/chroma_db"
COLLECTION_NAME = "catalogo_outfitly"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
DOCUMENTOS_PATH = "data/documentos_procesados.json"


def cargar_documentos(ruta: str) -> list:
    with open(ruta, encoding="utf-8") as f:
        return json.load(f)


def construir_indice(documentos: list, reset: bool = True) -> None:
    """
    Crea (o recrea) la colección de Chroma con los documentos de ingesta.

    Args:
        documentos: lista de {id, texto, metadata} generada por ingesta.py
        reset: si True, borra la colección existente antes de indexar
               (útil cuando el inventario cambió y quieres reconstruir
               todo desde cero en vez de ir acumulando duplicados)
    """
    Path(CHROMA_PATH).mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=CHROMA_PATH)

    embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=EMBEDDING_MODEL
    )

    if reset:
        try:
            client.delete_collection(COLLECTION_NAME)
        except Exception:
            pass  # no existía todavía, no pasa nada

    coleccion = client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=embedding_fn,
    )

    ids = [str(doc["id"]) for doc in documentos]
    textos = [doc["texto"] for doc in documentos]
    metadatas = [doc["metadata"] for doc in documentos]

    # Chroma no acepta bien tandas gigantes de una sola vez en algunos setups,
    # así que lo mandamos en lotes por seguridad
    BATCH_SIZE = 100
    for i in range(0, len(ids), BATCH_SIZE):
        coleccion.add(
            ids=ids[i:i + BATCH_SIZE],
            documents=textos[i:i + BATCH_SIZE],
            metadatas=metadatas[i:i + BATCH_SIZE],
        )

    print(f"[create_vector_index] {len(ids)} productos indexados en '{COLLECTION_NAME}'")


if __name__ == "__main__":
    documentos = cargar_documentos(DOCUMENTOS_PATH)
    construir_indice(documentos, reset=True)