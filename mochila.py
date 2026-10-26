"""Problema de la mochila 0/1 con dos límites: peso máximo (kg) y volumen máximo (m³)."""
import math

PASOS_VOL = 40  # el volumen del vehículo se divide en 40 partes iguales


def volumen(p):
    """Volumen de la caja en m³ a partir de alto, ancho y profundidad (cm)."""
    return p["alto"] * p["ancho"] * p["profundidad"] / 1_000_000


def mochila(items, peso_max, vol_max):
    """Elige los paquetes de un viaje maximizando la tarifa total sin pasar el peso ni el volumen."""
    n = len(items)
    unidad = vol_max / PASOS_VOL  # m³ que vale cada parte del volumen
    # Se redondea hacia arriba para no pasarse nunca de la capacidad
    pesos = [math.ceil(p["peso"]) for p in items]
    vols = [math.ceil(volumen(p) / unidad - 1e-9) for p in items]

    # t[i][w][u] = mejor tarifa con los primeros i paquetes, hasta w kg y hasta u partes de volumen
    t = [[[0] * (PASOS_VOL + 1) for _ in range(peso_max + 1)] for _ in range(n + 1)]
    for i in range(1, n + 1):
        p, c, v = pesos[i - 1], vols[i - 1], items[i - 1]["valor"]
        for w in range(peso_max + 1):
            for u in range(PASOS_VOL + 1):
                t[i][w][u] = t[i - 1][w][u]                      # no llevar el paquete i
                if p <= w and c <= u:                            # llevarlo, si cabe en peso y volumen
                    t[i][w][u] = max(t[i][w][u], t[i - 1][w - p][u - c] + v)

    # Reconstrucción: recorre la tabla hacia atrás para saber cuáles se eligieron
    elegidos, w, u = [], peso_max, PASOS_VOL
    for i in range(n, 0, -1):
        if t[i][w][u] != t[i - 1][w][u]:
            elegidos.append(items[i - 1])
            w -= pesos[i - 1]
            u -= vols[i - 1]
    return elegidos[::-1]
