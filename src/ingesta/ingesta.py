import tempfile
from pathlib import Path
from git import Repo
from markitdown import MarkItDown
from src.utils.embeddings import EmbeddingClient
from src.utils.mongodb import MongoDBClient
"""
ingesta.py
Lee el catálogo/inventario de la tienda (CSV o JSON) y lo transforma en
documentos de texto listos para vectorizar en create_vector_index.py

Formato de entrada esperado (catalogo.csv):
id,nombre,categoria,color,talla,stock,precio,descripcion
1,Polera oversize,Poleras,Negro,M,8,15990,"Polera de algodón corte oversize, ideal streetwear"
2,Jeans slim fit,Pantalones,Azul,32,0,29990,"Jeans slim fit tiro medio"
...
"""

import csv
import json
from pathlib import Path
from typing import List, Dict


def cargar_catalogo_csv(ruta: str) -> List[Dict]:
    """Carga el catálogo desde un CSV y lo devuelve como lista de dicts."""
    productos = []
    with open(ruta, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for fila in reader:
            fila["stock"] = int(fila.get("stock", 0))
            fila["precio"] = float(fila.get("precio", 0))
            productos.append(fila)
    return productos


def cargar_catalogo_json(ruta: str) -> List[Dict]:
    """Alternativa si el inventario viene como JSON (ej. export de un ERP/API)."""
    with open(ruta, encoding="utf-8") as f:
        return json.load(f)


def construir_documento(producto: Dict) -> str:
    """
    Convierte un producto en un texto natural, que es lo que realmente
    se va a vectorizar. Mientras más descriptivo, mejor el retrieval.
    """
    return (
        f"{producto['nombre']} - Categoría: {producto['categoria']}. "
        f"Color: {producto['color']}. Talla: {producto['talla']}. "
        f"Precio: ${producto['precio']:.0f}. "
        f"Stock disponible: {producto['stock']} unidades. "
        f"{producto.get('descripcion', '')}"
    ).strip()


def filtrar_disponibles(productos: List[Dict]) -> List[Dict]:
    """
    Filtra productos sin stock. Clave para que el bot nunca recomiende
    algo que no está disponible: si no pasa por acá, nunca llega al LLM.
    """
    return [p for p in productos if p["stock"] > 0]


def preparar_documentos(productos: List[Dict], solo_disponibles: bool = True) -> List[Dict]:
    """
    Devuelve una lista de dicts {id, texto, metadata} lista para
    create_vector_index.py. metadata guarda los datos estructurados
    para poder mostrarlos después en la UI sin volver a parsear texto.
    """
    if solo_disponibles:
        productos = filtrar_disponibles(productos)

    documentos = []
    for p in productos:
        documentos.append({
            "id": p.get("id"),
            "texto": construir_documento(p),
            "metadata": {
                "nombre": p.get("nombre"),
                "categoria": p.get("categoria"),
                "color": p.get("color"),
                "talla": p.get("talla"),
                "precio": p.get("precio"),
                "stock": p.get("stock"),
            },
        })
    return documentos


def guardar_documentos(documentos: List[Dict], ruta_salida: str) -> None:
    Path(ruta_salida).parent.mkdir(parents=True, exist_ok=True)
    with open(ruta_salida, "w", encoding="utf-8") as f:
        json.dump(documentos, f, ensure_ascii=False, indent=2)
    print(f"[ingesta] {len(documentos)} documentos guardados en {ruta_salida}")


if __name__ == "__main__":
    # Ajusta las rutas según dónde guardes tu catálogo real
    productos = cargar_catalogo_csv("data/catalogo.csv")
    documentos = preparar_documentos(productos, solo_disponibles=True)
    guardar_documentos(documentos, "data/documentos_procesados.json")