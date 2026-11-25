(() => {
  const status = document.getElementById('map-status');
  if (!window.L) { status.textContent = 'El mapa no está disponible. Puedes explorar todas las actividades en la lista.'; return; }
  const map = L.map('map').setView([-41.39, -72.94], 11);
  const tiles = L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {maxZoom: 19, attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'}).addTo(map);
  tiles.on('tileerror', () => { status.textContent = 'No se pudo cargar parte del mapa. La lista y las fichas siguen disponibles.'; });
  const activities = JSON.parse(document.getElementById('map-data').textContent);
  const points = [];
  activities.forEach(a => {
    const link = document.createElement('a'); link.textContent = a.title; link.href = a.url;
    L.marker([a.lat, a.lng]).addTo(map).bindPopup(link); points.push([a.lat, a.lng]);
  });
  if (points.length) map.fitBounds(points, {padding: [35, 35], maxZoom: 13});
})();
