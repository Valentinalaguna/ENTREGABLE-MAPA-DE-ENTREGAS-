// Interfaz: vehículo, peso, destino en el mapa, rutas y despacho
const $ = id => document.getElementById(id);
let cfg, destino = null, rutas = [], elegida = 0, pedidos = [], n = 0;

async function api(url, cuerpo) {
  const r = await fetch(url, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(cuerpo) });
  return r.json();
}
const veh = () => cfg.vehiculos[$("vehiculo").value];

function cargarVehiculo() {
  $("pesoMax").value = veh().peso_max;
  $("volMax").value = veh().vol_max;
  revisarPeso();
  calcular();
}

const volumenCaja = () => $("alto").value * $("ancho").value * $("prof").value / 1e6; // cm³ -> m³

function revisarPeso() { // avisa si el paquete no cabe (peso o volumen) y sugiere el vehículo más pequeño que sí lo lleva
  const peso = +$("peso").value, max = +$("pesoMax").value, vol = volumenCaja(), volMax = +$("volMax").value;
  const ok = Object.values(cfg.vehiculos).sort((a, b) => a.peso_max - b.peso_max)
    .find(v => peso <= v.peso_max && vol <= v.vol_max);
  $("aviso").textContent = peso > max || vol > volMax
    ? `${veh().nombre} no carga este paquete (${peso} kg, ${vol.toFixed(3)} m³; máx. ${max} kg y ${volMax} m³). ` + (ok ? `Usa ${ok.nombre}.` : "Supera todos los vehículos.")
    : `${veh().nombre} puede llevar este paquete (${vol.toFixed(3)} m³).`;
}

async function calcular(ajustar = false) {
  if (!destino) return;
  const d = await api("/api/rutas", { lat: destino.lat, lon: destino.lng, vehiculo: $("vehiculo").value });
  rutas = d.rutas || []; elegida = 0;
  $("fuente").textContent = d.error || "";
  if (d.error) { Mapa.destino(null); destino = null; }
  pintarRutas(true);
}

function pintarRutas(ajustar = false) {
  $("rutas").innerHTML = rutas.length
    ? rutas.map((r, i) => `<button type="button" class="ruta${i === elegida ? " activa" : ""}" data-i="${i}">
        <b>${r.min} min</b>, ${r.km} km<br><small>${r.nombre}</small></button>`).join("")
    : "<small>No hay ruta hasta ese punto.</small>";
  Mapa.rutas(rutas, elegida, i => { elegida = i; pintarRutas(); }, ajustar, destino);
}

function pintarPedidos() {
  $("totalPedidos").textContent = pedidos.length;
  $("pesoPedidos").textContent = pedidos.reduce((s, p) => s + p.peso, 0).toFixed(1) + " kg";
  $("lista").innerHTML = pedidos.map(p => `<li>${esc(p.nombre)}, ${p.peso} kg, ${p.alto}x${p.ancho}x${p.profundidad} cm
    <button data-id="${p.id}" aria-label="Quitar ${esc(p.nombre)}">×</button></li>`).join("");
  Mapa.pedidos(pedidos);
}

$("rutas").addEventListener("click", e => {
  const b = e.target.closest("[data-i]");
  if (b) { elegida = +b.dataset.i; pintarRutas(); }
});
$("lista").addEventListener("click", e => {
  const id = +e.target.dataset.id;
  if (id) { pedidos = pedidos.filter(p => p.id !== id); pintarPedidos(); }
});
["vehiculo"].forEach(id => $(id).addEventListener("change", cargarVehiculo));
["peso", "pesoMax", "alto", "ancho", "prof", "volMax"].forEach(id => $(id).addEventListener("input", revisarPeso));

$("guardar").addEventListener("click", () => {
  const peso = +$("peso").value;
  if (!destino || !rutas.length || !(peso > 0)) return alert("Elige un destino válido dentro de Ibagué e ingresa el peso.");
  const alto = +$("alto").value, ancho = +$("ancho").value, profundidad = +$("prof").value;
  if (!(alto > 0 && ancho > 0 && profundidad > 0)) return alert("Ingresa alto, ancho y profundidad de la caja.");
  pedidos.push({ id: ++n, nombre: $("nombre").value.trim() || `Paquete ${n}`, peso, valor: +$("valor").value || 1,
                 alto, ancho, profundidad, lat: destino.lat, lon: destino.lng });
  $("nombre").value = "";
  pintarPedidos();
});

$("despachar").addEventListener("click", async () => {
  if (!pedidos.length) return alert("Guarda al menos un pedido.");
  const max = +$("pesoMax").value, color = veh().color;
  const d = await api("/api/despacho", { pedidos, vehiculo: $("vehiculo").value,
                                          peso_max: max, vol_max: +$("volMax").value });
  if (d.error) return alert(d.error);
  Mapa.viajes(d.viajes, color, pedidos);
  $("resultado").innerHTML = d.viajes.map(v => `<article style="border-color:${color}"><h3>${v.nombre}</h3>
    <p>${v.peso} de ${max} kg, ${v.vol} de ${$("volMax").value} m³, ${v.orden.length} paquetes, ${v.km} km, ${v.min} min</p>
    <ol>${v.orden.map(p => `<li>${esc(p.nombre)} <small>${p.peso} kg</small></li>`).join("")}</ol></article>`).join("")
    + (d.sin_asignar.length ? `<p>No salen (superan el peso o volumen máximo): ${d.sin_asignar.map(esc).join(", ")}.</p>` : "");
});

fetch("/api/config").then(r => r.json()).then(c => {
  cfg = c;
  Mapa.init(c.bodega, c.contorno, ll => { destino = ll; Mapa.destino(ll); calcular(); });
  cargarVehiculo();
});
