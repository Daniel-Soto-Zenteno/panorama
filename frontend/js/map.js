const map = L.map("map").setView([-41.4693, -72.9424], 12);

L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
  attribution: "&copy; OpenStreetMap contributors"
}).addTo(map);

// Marcador de prueba inicial
L.marker([-41.3195, -72.9854])
  .addTo(map)
  .bindPopup("<strong>Punto de encuentro de prueba</strong><br>Puerto Varas")
  .openPopup();