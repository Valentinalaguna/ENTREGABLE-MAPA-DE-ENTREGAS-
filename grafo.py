"""Calles de Ibagué: descarga el mapa de OpenStreetMap y lo convierte en un grafo."""
import math
import os
import pickle

from datos import CENTRO, MAX_SNAP_M, RADIO_M

ARCHIVO = "ibague_grafo_v4.pkl"


def cargar():
    """Devuelve (nodos, ady).
    nodos[id] = (lat, lon)  -> cada esquina
    ady[u][v] = {"m": metros, "tipo": tipo de vía, "geom": puntos de la calle}  -> cada calle de u a v"""
    if os.path.exists(ARCHIVO):
        with open(ARCHIVO, "rb") as f:
            nodos, ady = pickle.load(f)[:2]
        return nodos, ady

    import networkx as nx
    import osmnx as ox
    print("Descargando calles de Ibagué (solo la primera vez, puede tardar varios minutos)...")
    G = ox.graph_from_point(CENTRO, dist=RADIO_M, network_type="drive")
    # Nos quedamos solo con la red conectada, para que siempre exista ruta entre dos esquinas
    G = G.subgraph(max(nx.strongly_connected_components(G), key=len))

    nodos = {n: (d["y"], d["x"]) for n, d in G.nodes(data=True)}
    ady = {n: {} for n in nodos}
    for u, v, d in G.edges(data=True):
        tipo = d.get("highway")
        tipo = tipo[0] if isinstance(tipo, list) else tipo
        geom = [(la, lo) for lo, la in d["geometry"].coords] if "geometry" in d else [nodos[u], nodos[v]]
        if u != v and (v not in ady[u] or d["length"] < ady[u][v]["m"]):
            ady[u][v] = {"m": d["length"], "tipo": tipo, "geom": geom}

    with open(ARCHIVO, "wb") as f:
        pickle.dump((nodos, ady), f)
    return nodos, ady


def limite_mapa(nodos):
    """Rectángulo que encierra todas las esquinas: sirve para delimitar el mapa."""
    lats = [p[0] for p in nodos.values()]
    lons = [p[1] for p in nodos.values()]
    sur, norte, oeste, este = min(lats), max(lats), min(lons), max(lons)
    return [(sur, oeste), (sur, este), (norte, este), (norte, oeste)]


def _metros(p, q):
    """Distancia aproximada en metros entre dos puntos (lat, lon)."""
    return math.hypot((q[0] - p[0]) * 110574, (q[1] - p[1]) * 111320 * math.cos(math.radians(p[0])))


def nodo_cercano(nodos, lat, lon):
    """Esquina más cercana a un punto."""
    return min(nodos, key=lambda n: _metros((lat, lon), nodos[n]))


def punto_cercano(nodos, lat, lon):
    """Esquina más cercana al clic, o None si está a más de MAX_SNAP_M metros."""
    n = nodo_cercano(nodos, lat, lon)
    d = _metros((lat, lon), nodos[n])
    if d > MAX_SNAP_M:
        return None
    return {"u": n, "lat": nodos[n][0], "lon": nodos[n][1], "dist": round(d)}
