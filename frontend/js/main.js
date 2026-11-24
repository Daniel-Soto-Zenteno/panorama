(() => {
  let activities = [];
  let currentUser = null; // { authenticated, username, is_admin }
  let referencePoint = { lat: -41.4718, lng: -72.9369 };
  let csrfToken = "";

  const authStatus = document.getElementById("auth-status");
  const btnOpenLogin = document.getElementById("btn-open-login");
  const btnLogout = document.getElementById("btn-logout");
  const loginPanel = document.getElementById("login-panel");
  const loginForm = document.getElementById("login-form");
  const btnCancelLogin = document.getElementById("btn-cancel-login");
  const loginMessage = document.getElementById("login-message");

  const filterZone = document.getElementById("filter-zone");
  const filterCategory = document.getElementById("filter-category");
  const filterRadius = document.getElementById("filter-radius");
  const btnUseLocation = document.getElementById("btn-use-location");
  const btnResetFilters = document.getElementById("btn-reset-filters");
  const resultsCount = document.getElementById("results-count");

  const adminPanel = document.getElementById("admin-panel");
  const activityForm = document.getElementById("activity-form");
  const activityIdInput = document.getElementById("activity-id");
  const activityTitleInput = document.getElementById("activity-title");
  const activityCategoryInput = document.getElementById("activity-category");
  const activityZoneInput = document.getElementById("activity-zone");
  const activityLatInput = document.getElementById("activity-lat");
  const activityLngInput = document.getElementById("activity-lng");
  const activityDateInput = document.getElementById("activity-date");
  const activityDescriptionInput = document.getElementById("activity-description");
  const activityFeaturedInput = document.getElementById("activity-featured");
  const btnClearForm = document.getElementById("btn-clear-form");
  const btnDeleteActivity = document.getElementById("btn-delete-activity");

  async function ensureCsrf() {
    if (csrfToken) return csrfToken;
    const res = await fetch("/api/csrf/", { credentials: "same-origin" });
    const data = await res.json();
    csrfToken = data.csrfToken || "";
    return csrfToken;
  }

  async function apiRequest(url, options = {}) {
    const method = (options.method || "GET").toUpperCase();
    const headers = { ...(options.headers || {}) };

    if (options.body && !headers["Content-Type"]) {
      headers["Content-Type"] = "application/json";
    }
    if (["POST", "PUT", "PATCH", "DELETE"].includes(method)) {
      const token = await ensureCsrf();
      headers["X-CSRFToken"] = token;
    }

    const res = await fetch(url, {
      credentials: "same-origin",
      ...options,
      headers,
    });

    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
      throw new Error(data.error || `Error HTTP ${res.status}`);
    }
    return data;
  }

  async function loadActivities() {
    const params = new URLSearchParams();
    if (filterZone.value !== "all") params.set("zone", filterZone.value);
    if (filterCategory.value !== "all") params.set("category", filterCategory.value);

    const query = params.toString() ? `?${params.toString()}` : "";
    const data = await apiRequest(`/api/activities/${query}`);
    activities = data.activities || [];
    refreshMap();
  }

  async function loadSession() {
    const data = await apiRequest("/api/session/");
    currentUser = data.authenticated ? data : null;
    updateAuthUI();
  }

  function getFilteredActivities() {
    const radius = filterRadius.value === "all" ? null : Number(filterRadius.value);

    return activities.filter((act) => {
      if (radius !== null && referencePoint) {
        const dist = PanoramaMap.distanceKm(
          referencePoint.lat,
          referencePoint.lng,
          act.lat,
          act.lng
        );
        if (dist > radius) return false;
      }
      return true;
    });
  }

  function refreshMap() {
    const filtered = getFilteredActivities();
    const isAdmin = Boolean(currentUser && currentUser.is_admin);
    resultsCount.textContent = `${filtered.length} ${
      filtered.length === 1 ? "actividad visible" : "actividades visibles"
    }`;
    PanoramaMap.renderActivities(filtered, isAdmin);
  }

  function updateAuthUI() {
    const isAdmin = Boolean(currentUser && currentUser.is_admin);
    if (currentUser) {
      authStatus.textContent = `${currentUser.username} (${isAdmin ? "Admin" : "Usuario"})`;
      btnOpenLogin.hidden = true;
      btnLogout.hidden = false;
      loginPanel.hidden = true;
    } else {
      authStatus.textContent = "Invitado";
      btnOpenLogin.hidden = false;
      btnLogout.hidden = true;
    }
    adminPanel.hidden = !isAdmin;
    refreshMap();
  }

  function resetActivityForm() {
    activityIdInput.value = "";
    activityTitleInput.value = "";
    activityCategoryInput.value = "Deportes";
    activityZoneInput.value = "puerto-montt";
    activityLatInput.value = "";
    activityLngInput.value = "";
    activityDateInput.value = "";
    activityDescriptionInput.value = "";
    activityFeaturedInput.checked = false;
    btnDeleteActivity.hidden = true;
  }

  function loadActivityIntoForm(act) {
    adminPanel.hidden = false;
    activityIdInput.value = act.id;
    activityTitleInput.value = act.title;
    activityCategoryInput.value = act.category;
    activityZoneInput.value = act.zone;
    activityLatInput.value = act.lat;
    activityLngInput.value = act.lng;
    activityDateInput.value = act.date || "";
    activityDescriptionInput.value = act.description || "";
    activityFeaturedInput.checked = Boolean(act.featured);
    btnDeleteActivity.hidden = false;
  }

  // Autenticación
  btnOpenLogin.addEventListener("click", () => {
    loginMessage.textContent = "";
    loginPanel.hidden = false;
  });

  btnCancelLogin.addEventListener("click", () => {
    loginPanel.hidden = true;
  });

  btnLogout.addEventListener("click", async () => {
    await apiRequest("/api/logout/", { method: "POST" });
    currentUser = null;
    resetActivityForm();
    updateAuthUI();
  });

  loginForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    loginMessage.textContent = "";
    const username = document.getElementById("login-user").value.trim();
    const password = document.getElementById("login-password").value;

    try {
      const data = await apiRequest("/api/login/", {
        method: "POST",
        body: JSON.stringify({ username, password }),
      });
      currentUser = data;
      loginForm.reset();
      updateAuthUI();
    } catch (err) {
      loginMessage.textContent = err.message;
    }
  });

  // Filtros
  [filterZone, filterCategory].forEach((el) => {
    el.addEventListener("change", () => {
      loadActivities().catch((err) => console.error(err));
    });
  });

  filterRadius.addEventListener("change", refreshMap);

  btnUseLocation.addEventListener("click", () => {
    if (!navigator.geolocation) {
      alert("Tu navegador no soporta geolocalización.");
      return;
    }
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        referencePoint = {
          lat: pos.coords.latitude,
          lng: pos.coords.longitude,
        };
        PanoramaMap.setUserLocation(referencePoint.lat, referencePoint.lng);
        if (filterRadius.value === "all") {
          filterRadius.value = "10";
        }
        refreshMap();
      },
      () => {
        alert("No se pudo obtener la ubicación.");
      }
    );
  });

  btnResetFilters.addEventListener("click", () => {
    filterZone.value = "all";
    filterCategory.value = "all";
    filterRadius.value = "all";
    loadActivities().catch((err) => console.error(err));
  });

  // CRUD de actividades (admin)
  activityForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    if (!currentUser || !currentUser.is_admin) return;

    const id = activityIdInput.value ? Number(activityIdInput.value) : null;
    const payload = {
      title: activityTitleInput.value.trim(),
      category: activityCategoryInput.value,
      zone: activityZoneInput.value,
      lat: Number(activityLatInput.value),
      lng: Number(activityLngInput.value),
      date: activityDateInput.value || null,
      description: activityDescriptionInput.value.trim(),
      featured: activityFeaturedInput.checked,
    };

    try {
      if (id) {
        await apiRequest(`/api/activities/${id}/`, {
          method: "PATCH",
          body: JSON.stringify(payload),
        });
      } else {
        await apiRequest("/api/activities/", {
          method: "POST",
          body: JSON.stringify(payload),
        });
      }
      resetActivityForm();
      await loadActivities();
    } catch (err) {
      alert(err.message);
    }
  });

  btnClearForm.addEventListener("click", resetActivityForm);

  btnDeleteActivity.addEventListener("click", async () => {
    if (!currentUser || !currentUser.is_admin) return;
    const id = Number(activityIdInput.value);
    if (!id) return;

    try {
      await apiRequest(`/api/activities/${id}/`, { method: "DELETE" });
      resetActivityForm();
      await loadActivities();
    } catch (err) {
      alert(err.message);
    }
  });

  // Inicialización
  PanoramaMap.init({
    onMapClick: (lat, lng) => {
      if (currentUser && currentUser.is_admin && !adminPanel.hidden) {
        activityLatInput.value = lat.toFixed(6);
        activityLngInput.value = lng.toFixed(6);
      }
    },
    onSelectActivity: (act) => {
      if (currentUser && currentUser.is_admin) {
        loadActivityIntoForm(act);
      }
    },
  });

  Promise.all([ensureCsrf(), loadSession(), loadActivities()]).catch((err) => {
    console.error("Error inicializando Panorama:", err);
  });
})();