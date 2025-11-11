import json
import os

def estado_salud_por_energia(energia):
    if energia <= 0:
        return "muerto"
    elif energia <= 25:
        return "moribundo"
    elif energia <= 50:
        return "mala"
    elif energia <= 75:
        return "buena"
    else:
        return "excelente"


def cargar_grafo_desde_json(ruta_json):
    """Genera un grafo en formato {nombre: {vecino: distancia}} desde Constellations.json."""
    if not os.path.exists(ruta_json):
        raise FileNotFoundError(f"No se encontró el archivo: {ruta_json}")

    with open(ruta_json, "r", encoding="utf-8") as f:
        data = json.load(f)

    grafo = {}
    for const in data.get("constellations", []):
        for star in const.get("starts", []):
            nombre = star["label"]
            grafo[nombre] = {}
            for enlace in star.get("linkedTo", []):
                if enlace.get("blocked", False):
                    continue
                destino_id = enlace["starId"]
                distancia = enlace["distance"]

                destino_nombre = None
                for c2 in data["constellations"]:
                    for s2 in c2["starts"]:
                        if s2["id"] == destino_id:
                            destino_nombre = s2["label"]
                            break
                    if destino_nombre:
                        break

                if destino_nombre:
                    grafo[nombre][destino_nombre] = distancia
    return grafo


def ruta_maxima(estrella_origen, salud_inicial, edad, burroenergia, pasto_bodega, grafo):
    """Calcula la ruta más larga posible antes de que el burro muera."""
    mejor_ruta = []
    max_estrellas = 0

    def dfs(actual, energia, pasto, visitadas):
        nonlocal mejor_ruta, max_estrellas
        if energia <= 0 or pasto <= 0:
            return
        if len(visitadas) > max_estrellas:
            mejor_ruta = visitadas.copy()
            max_estrellas = len(visitadas)

        for destino, distancia in grafo.get(actual, {}).items():
            if destino in visitadas:
                continue
            consumo_energia = distancia * 1.2
            consumo_pasto = distancia * 0.7
            nueva_energia = energia - consumo_energia
            nuevo_pasto = pasto - consumo_pasto
            if nueva_energia > 0 and nuevo_pasto > 0:
                dfs(destino, nueva_energia, nuevo_pasto, visitadas + [destino])

    dfs(estrella_origen, burroenergia, pasto_bodega, [estrella_origen])

    estado_final = estado_salud_por_energia(burroenergia - (100 - burroenergia))
    return {
        "ruta": mejor_ruta,
        "estrellas_visitadas": max_estrellas,
        "estado_final": estado_final,
        "energia_inicial": burroenergia,
        "pasto_inicial": pasto_bodega
    }
