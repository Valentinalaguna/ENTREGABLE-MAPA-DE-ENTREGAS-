"""Dijkstra sobre las calles de Ibagué, rutas hasta un destino y armado de los viajes."""
import heapq
import math

from datos import VELOCIDADES
from mochila import mochila, volumen


def dijkstra(ady, origen, costo, destino=None):
    """Mejor costo desde el origen a cada esquina. 'costo' es una función que dice cuánto cuesta cada calle."""
    dist, prev, cola = {origen: 0}, {}, [(0, origen)]
    while cola:
        d, u = heapq.heappop(cola)           # la esquina pendiente más cercana al origen
        if d > dist.get(u, math.inf):        # entrada vieja: ya se encontró un camino mejor
            continue
        if u == destino:                     # ya llegamos al destino, no hace falta seguir
            break
        for v, calle in ady[u].items():
            nd = d + costo(u, v, calle)
            if nd < dist.get(v, math.inf):   # ¿llegar a v por u es mejor que lo que se conocía?
                dist[v], prev[v] = nd, u
                heapq.heappush(cola, (nd, v))
    return dist, prev


def camino(prev, origen, destino):
    """Reconstruye la ruta (lista de esquinas) yendo hacia atrás con 'prev'."""
    if destino != origen and destino not in prev:
        return None                          # no hay ruta
    ruta = [destino]
    while ruta[-1] != origen:
        ruta.append(prev[ruta[-1]])
    return ruta[::-1]


def segundos(calle, veh):
    """Tiempo en segundos de recorrer una calle: distancia / velocidad (según tipo de vía y vehículo)."""
    metros_por_segundo = VELOCIDADES.get(calle["tipo"], 25) * veh["vel"] / 3.6
    return calle["m"] / metros_por_segundo


def describir(nombre, ruta, ady, veh):
    """Convierte una lista de esquinas en kilómetros, minutos y puntos para dibujar en el mapa."""
    metros = seg = 0
    coords = []
    for u, v in zip(ruta, ruta[1:]):
        calle = ady[u][v]
        metros += calle["m"]
        seg += segundos(calle, veh)
        coords += calle["geom"] if not coords else calle["geom"][1:]   # [1:] evita repetir el punto de unión
    return {"nombre": nombre, "km": round(metros / 1000, 1), "min": round(seg / 60), "coords": coords}


def rutas_alternativas(ady, origen, punto, veh):
    """Dos rutas hasta el destino: la más rápida (tiempo) y la más corta (metros)."""
    destino = punto["u"]

    def en_tiempo(u, v, calle):
        return segundos(calle, veh)

    def en_metros(u, v, calle):
        return calle["m"]

    rutas = []
    for nombre, costo in (("Más rápida", en_tiempo), ("Más corta", en_metros)):
        ruta = camino(dijkstra(ady, origen, costo, destino)[1], origen, destino)
        if ruta and len(ruta) > 1 and ruta not in [r for _, r in rutas]:   # no repetir si son la misma
            rutas.append((nombre, ruta))
    return [describir(nombre, ruta, ady, veh) for nombre, ruta in rutas]


def despachar(ady, deposito, pedidos, veh):
    """La mochila elige qué paquetes suben en cada viaje; después se visita siempre el más cercano."""
    def en_tiempo(u, v, calle):
        return segundos(calle, veh)

    # Solo los paquetes que caben solos en el vehículo (peso y volumen)
    pendientes = [p for p in pedidos if math.ceil(p["peso"]) <= veh["peso_max"] and volumen(p) <= veh["vol_max"]]
    viajes = []

    while pendientes:
        # 1. Mochila: qué paquetes suben en este viaje
        elegidos = mochila(pendientes, int(veh["peso_max"]), veh["vol_max"])
        if not elegidos:
            break

        # 2. Dijkstra: desde donde estamos, ir al paquete más cercano en tiempo, y repetir
        actual, esquinas, orden, faltan = deposito, [deposito], [], list(elegidos)
        while faltan:
            dist, prev = dijkstra(ady, actual, en_tiempo)
            siguiente = min(faltan, key=lambda p: dist[p["u"]])
            esquinas += camino(prev, actual, siguiente["u"])[1:]
            orden.append(siguiente)
            faltan.remove(siguiente)
            actual = siguiente["u"]

        # 3. Volver a la bodega
        prev = dijkstra(ady, actual, en_tiempo, deposito)[1]
        esquinas += camino(prev, actual, deposito)[1:]

        viaje = describir(f"Viaje {len(viajes) + 1}", esquinas, ady, veh)
        viaje.update(orden=orden, peso=sum(p["peso"] for p in orden),
                     vol=round(sum(volumen(p) for p in orden), 3), valor=sum(p["valor"] for p in orden))
        viajes.append(viaje)
        pendientes = [p for p in pendientes if p not in elegidos]

    llevados = {p["id"] for v in viajes for p in v["orden"]}
    return {"viajes": viajes, "sin_asignar": [p["nombre"] for p in pedidos if p["id"] not in llevados]}
