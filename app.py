"""Servidor Flask: recibe el clic del mapa, calcula rutas (Dijkstra) y arma los viajes (mochila)."""
import threading
import webbrowser

from flask import Flask, jsonify, request

from datos import BODEGA, VEHICULOS
from dijkstra import despachar, rutas_alternativas
from grafo import cargar, limite_mapa, nodo_cercano, punto_cercano

app = Flask(__name__, static_folder="static", static_url_path="/static")
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0
NODOS, ADY = cargar()                       # el grafo de calles
LIMITE = limite_mapa(NODOS)                 # borde del mapa
DEPOSITO = nodo_cercano(NODOS, *BODEGA)     # esquina donde sale cada viaje


def validar(lat, lon):
    """Devuelve (esquina_más_cercana, mensaje_de_error)."""
    punto = punto_cercano(NODOS, lat, lon)
    if not punto:
        return None, "No hay una calle cerca de ese punto. Haz clic más cerca de una vía."
    return punto, None


@app.get("/")
def inicio():
    return app.send_static_file("index.html")


@app.get("/api/config")
def config():
    return jsonify(vehiculos=VEHICULOS, bodega=NODOS[DEPOSITO], contorno=LIMITE)


@app.post("/api/rutas")
def rutas():
    d = request.get_json()
    veh = VEHICULOS[d["vehiculo"]]
    punto, error = validar(d["lat"], d["lon"])
    if error:
        return jsonify(error=error)
    return jsonify(rutas=rutas_alternativas(ADY, DEPOSITO, punto, veh))


@app.post("/api/despacho")
def despacho():
    d = request.get_json()
    veh = {**VEHICULOS[d["vehiculo"]], "peso_max": d["peso_max"], "vol_max": d["vol_max"]}
    pedidos = []
    for p in d["pedidos"]:
        punto, error = validar(p["lat"], p["lon"])
        if error:
            return jsonify(error=f"{p['nombre']}: {error}")
        pedidos.append({**p, "u": punto["u"], "lat": punto["lat"], "lon": punto["lon"]})
    return jsonify(despachar(ADY, DEPOSITO, pedidos, veh))


if __name__ == "__main__":
    print("Abre http://127.0.0.1:5050  (si ves un mapa viejo, cierra la ventana anterior de python)")
    threading.Timer(1, lambda: webbrowser.open("http://127.0.0.1:5050")).start()
    app.run(port=5050)
