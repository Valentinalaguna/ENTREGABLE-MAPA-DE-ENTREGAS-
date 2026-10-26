// Mapa con Leaflet: ruta elegida en azul y alternativas en gris
const esc = s => String(s).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

const Mapa = {
  init(centro, contorno, alClick) {
    const caja = L.latLngBounds(contorno);
    this.map = L.map("mapa", { maxBounds: caja.pad(0.02), maxBoundsViscosity: 1 });
    this.map.fitBounds(caja);
    this.map.setMinZoom(this.map.getZoom()); // no se puede alejar más que la vista completa de Ibagué
    L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", { maxZoom: 19, attribution: "© OpenStreetMap" }).addTo(this.map);
    // Máscara: tapa todo lo que está fuera de Ibagué y dibuja su contorno
    this.map.createPane("mascara").style.zIndex = 350;
    L.polygon([[[-85, -180], [-85, 180], [85, 180], [85, -180]], contorno],
      { pane: "mascara", stroke: false, fillColor: "#eef1ef", fillOpacity: 1, interactive: false }).addTo(this.map);
    L.polygon(contorno, { color: "#6757d9", weight: 2, fill: false, interactive: false }).addTo(this.map);
    this.capaR = L.layerGroup().addTo(this.map);
    this.capaP = L.layerGroup().addTo(this.map);
    L.marker(centro, { icon: this.pin("B", "#17233b") }).bindPopup("<b>Centro de despacho</b>").addTo(this.map);
    this.map.on("click", e => alClick(e.latlng));
  },
  pin(t, c) {
    return L.divIcon({ className: "", iconSize: [26, 26], iconAnchor: [13, 13],
      html: `<span class="pin" style="background:${c}">${t}</span>` });
  },
  destino(ll) { if (this.d) this.d.remove(); this.d = ll ? L.marker(ll).addTo(this.map) : null; },

  rutas(rutas, sel, alElegir, ajustar, clic) {
    this.capaR.clearLayers();
    rutas.forEach((r, i) => { if (i !== sel) L.polyline(r.coords, { color: "#a8b2c3", weight: 6 }).on("click", () => alElegir(i)).addTo(this.capaR); });
    const r = rutas[sel];
    if (!r) return;
    L.polyline(r.coords, { color: "#4e40b5", weight: 10 }).addTo(this.capaR);
    L.polyline(r.coords, { color: "#897cf0", weight: 5 }).addTo(this.capaR);
    if (clic) { // tramo punteado entre el final de la ruta (sobre la calle) y el punto donde hiciste clic
      L.polyline([r.coords[r.coords.length - 1], [clic.lat, clic.lng]], { color: "#475569", weight: 3, dashArray: "4 6" }).addTo(this.capaR);
    }
    if (ajustar) this.map.fitBounds(L.polyline(r.coords).getBounds(), { padding: [40, 40] });
  },

  pedidos(pedidos) {
    this.capaP.clearLayers();
    pedidos.forEach((p, i) => this.marcador(p, i + 1, "#a8b2c3", "Pendiente"));
  },
  marcador(p, t, color, estado) {
    L.marker([p.lat, p.lon], { icon: this.pin(t, color) }).bindPopup(
      `<b>${esc(p.nombre)}</b><br>Peso: ${p.peso} kg<br>Caja: ${p.alto}x${p.ancho}x${p.profundidad} cm<br>Destino: ${p.lat.toFixed(4)}, ${p.lon.toFixed(4)}<br>${estado}`).addTo(this.capaP);
  },
  viajes(viajes, color, pedidos) {
    this.capaR.clearLayers(); this.capaP.clearLayers();
    const asignado = new Set();
    viajes.forEach((v, i) => {
      L.polyline(v.coords, { color, weight: 5, dashArray: i % 2 ? "10 8" : null })
        .bindPopup(`<b>${v.nombre}</b><br>${v.km} km, ${v.min} min, ${v.peso} kg`).addTo(this.capaR);
      v.orden.forEach((p, j) => { asignado.add(p.id); this.marcador(p, j + 1, color, `${v.nombre}, parada ${j + 1}`); });
    });
    pedidos.filter(p => !asignado.has(p.id)).forEach(p => this.marcador(p, "-", "#a8b2c3", "Pendiente de asignación"));
  }
};
