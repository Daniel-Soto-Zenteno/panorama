const PanoramaMap = (() => {
  let map;
  let markersLayer;
  let userMarker;
  let onMapClickCallback = null;
  let onSelectActivityCallback = null;

  const DEFAULT_CENTER = [-41.39, -72.92];
  const DEFAULT_ZOOM = 11;

  function init({ onMapClick, onSelectActivity }) {
    onMapClickCallback = onMapClick;
    onSelectActivityCallback = onSelectActivity;

    map = L.map("map").setView(DEFAULT_CENTER, DEFAULT_ZOOM);

    L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
          maxZoom: 19,
          attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        }).addTo(map);

    markersLayer = L.layerGroup().addTo(map);

    map.on("click", (e) => {
      if (typeof onMapClickCallback === "function") {
        onMapClickCallback(e.latlng.lat, e.latlng.lng);
      }
    });
  }

  function distanceKm(lat1, lon1, lat2, lon2) {
    const R = 6371;
    const toRad = (deg) => (deg * Math.PI) / 180;
    const dLat = toRad(lat2 - lat1);
    const dLon = toRad(lon2 - lon1);
    const a =
      Math.sin(dLat / 2) ** 2 +
      Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) * Math.sin(dLon / 2) ** 2;
    return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  }

  function setUserLocation(lat, lng) {
    if (userMarker) {
      map.removeLayer(userMarker);
    }
    userMarker = L.circleMarker([lat, lng], { radius: 8 }).addTo(map);
    userMarker.bindPopup("Tu ubicación de referencia").openPopup();
    map.setView([lat, lng], 13);
  }

  function renderActivities(activities, isAdmin) {
    markersLayer.clearLayers();

    activities.forEach((act) => {
      const marker = L.marker([act.lat, act.lng]);

      const container = document.createElement("div");
      const title = document.createElement("strong");
      title.textContent = act.featured ? `★ ${act.title}` : act.title;

      const timing = document.createElement("div");
      if (act.all_year) {
        timing.textContent = act.schedule ? `Todo el año · ${act.schedule}` : "Todo el año";
      } else if (act.date) {
        timing.textContent = `Fecha: ${act.date.replace("T", " ")}`;
      }
      if (timing.textContent) container.appendChild(timing);

      const meta = document.createElement("div");
      meta.textContent = `${act.category} · ${act.zone === "puerto-varas" ? "Puerto Varas" : "Puerto Montt"}`;

      const desc = document.createElement("p");
      desc.textContent = act.description || "";

      container.appendChild(title);
      container.appendChild(meta);
      if (act.description) container.appendChild(desc);

      if (isAdmin) {
        const editBtn = document.createElement("button");
        editBtn.type = "button";
        editBtn.textContent = "Editar actividad";
        editBtn.addEventListener("click", () => {
          if (typeof onSelectActivityCallback === "function") {
            onSelectActivityCallback(act);
          }
        });
        container.appendChild(editBtn);
      }

      marker.bindPopup(container);
      marker.addTo(markersLayer);
    });
  }

  return {
    init,
    distanceKm,
    setUserLocation,
    renderActivities,
  };
})();