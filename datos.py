"""Datos de la simulación de entregas en Ibagué."""
CENTRO = (4.4300, -75.2100)   # centro del área de calles que se descarga
RADIO_M = 13000               # radio de calles a descargar (metros)
BODEGA = (4.4234, -75.1864)   # Punto de salida del modelo (coordenadas aproximadas, se puede ajustar)

# peso_max en kg, vol_max en m³ (capacidad aproximada: puedes cambiarla)
# vel = factor de velocidad del vehículo (1.0 = velocidad normal de la vía)
VEHICULOS = {
    "moto":   {"nombre": "Moto",   "peso_max": 25,   "vol_max": 0.08, "color": "#e38b43", "vel": 1.0},
    "van":    {"nombre": "Van",    "peso_max": 600,  "vol_max": 6,    "color": "#6757d9", "vel": 0.95},
    "furgon": {"nombre": "Furgón", "peso_max": 1200, "vol_max": 12,   "color": "#19a88b", "vel": 0.85},
}

VELOCIDADES = {"trunk": 60, "primary": 45, "secondary": 38, "tertiary": 32,
               "unclassified": 28, "residential": 25}     # km/h por tipo de vía

MAX_SNAP_M = 300   # distancia máxima permitida entre el clic y la esquina más cercana (m)
