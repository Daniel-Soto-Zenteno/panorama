(() => {
  "use strict";
  const $ = (id) => document.getElementById(id),
    CATEGORIES = {
      sport: { name: "Deportes", icon: "sport" },
      outdoor: { name: "Aire libre", icon: "tree" },
      culture: { name: "Arte y cultura", icon: "culture" },
      local: { name: "Ferias y barrio", icon: "market" },
    };
  const PATHS = {
    search: '<circle cx="10.5" cy="10.5" r="6.5"/><path d="m16 16 4 4"/>',
    pin: '<path d="M19 10c0 5-7 11-7 11S5 15 5 10a7 7 0 1 1 14 0Z"/><circle cx="12" cy="10" r="2.5"/>',
    map: '<path d="m3 6 6-3 6 3 6-3v15l-6 3-6-3-6 3Z"/><path d="M9 3v15M15 6v15"/>',
    chat: '<path d="M21 11a9 9 0 0 1-9 9H4l-3 2 2-6a9 9 0 1 1 18-5Z"/><path d="M7 9h10M7 13h6"/>',
    users:
      '<circle cx="9" cy="8" r="3.5"/><path d="M2 21v-2a7 7 0 0 1 14 0v2M16 5a3.5 3.5 0 0 1 0 7M19 16a5 5 0 0 1 3 5"/>',
    user: '<circle cx="12" cy="8" r="4"/><path d="M4 21v-2a8 8 0 0 1 16 0v2"/>',
    plus: '<path d="M12 4v16M4 12h16"/>',
    chevron: '<path d="m14 5-7 7 7 7"/>',
    close: '<path d="m6 6 12 12M6 18 18 6"/>',
    save: '<path d="M6 3h12v19l-6-4-6 4Z"/>',
    clock: '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l4 2"/>',
    star: '<path d="m12 3 2.8 5.7 6.2.9-4.5 4.4 1.1 6.2L12 17.3l-5.6 2.9 1.1-6.2L3 9.6l6.2-.9L12 3Z"/>',
    share: '<path d="m14 3 7 7-7 7v-4c-6 0-9 3-11 7 0-8 3-13 11-13V3Z"/>',
    sport:
      '<circle cx="12" cy="12" r="9"/><path d="M4 7c7 1 11 5 13 12M7 4c1 7 5 11 12 13M3 13 13 3M11 21l10-10"/>',
    culture:
      '<path d="m3 9 9-6 9 6M3 21h18M5 10v8M10 10v8M14 10v8M19 10v8M3 18h18"/>',
    tree: '<path d="m12 2-6 8h3l-5 7h16l-5-7h3L12 2ZM12 17v5"/>',
    market:
      '<path d="M3 9h18l-2-6H5L3 9Zm1 0v12h16V9M8 21v-7h8v7M3 9c0 4 5 4 5 0 0 4 8 4 8 0 0 4 5 4 5 0"/>',
    filters:
      '<path d="M3 6h7M14 6h7M3 12h3M10 12h11M3 18h10M17 18h4"/><circle cx="12" cy="6" r="2"/><circle cx="8" cy="12" r="2"/><circle cx="15" cy="18" r="2"/>',
    locate:
      '<circle cx="12" cy="12" r="6"/><path d="M12 2v4M12 18v4M2 12h4M18 12h4"/>',
    layers:
      '<path d="m12 3 10 5-10 5L2 8l10-5ZM2 12l10 5 10-5M2 16l10 5 10-5"/>',
    check: '<path d="m5 12 4 4L19 6"/>',
    shield:
      '<path d="m12 3 8 3v6c0 5-8 10-8 10S4 17 4 12V6l8-3Z"/><path d="m8 12 3 3 5-6"/>',
    flag: '<path d="M5 22V3c4-3 9 3 14 0v11c-5 3-10-3-14 0"/>',
    edit: '<path d="m15 4 5 5M4 20l5-1L21 7a2.8 2.8 0 0 0-4-4L5 15l-1 5Z"/>',
    leaf: '<path d="M21 3c-10-2-19 3-17 12 1 5 7 6 11 3 4-3 4-8 6-15ZM4 21 15 9"/>',
    bolt: '<path d="m13 2-9 12h7l-1 8 10-13h-7V2Z"/>',
  };
  function el(tag, cls, text) {
    const e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text !== undefined) e.textContent = text;
    return e;
  }
  function icon(name) {
    const s = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    s.setAttribute("class", "icon");
    s.setAttribute("viewBox", "0 0 24 24");
    s.setAttribute("aria-hidden", "true");
    s.innerHTML = PATHS[name] || PATHS.pin;
    return s;
  }
  function btn(text, name, cls, fn) {
    const b = el("button", cls);
    b.type = "button";
    if (name) b.append(icon(name));
    if (text) b.append(document.createTextNode(text));
    if (fn) b.onclick = fn;
    return b;
  }
  function mark(category) {
    const e = el("span", "topic-mark");
    e.append(icon(CATEGORIES[category]?.icon || "users"));
    return e;
  }
  function fact(name, text, cls) {
    const e = el("p", cls);
    e.append(icon(name), document.createTextNode(text));
    return e;
  }
  function initials(name) {
    return name
      .trim()
      .split(/\s+/)
      .slice(0, 2)
      .map((n) => n[0])
      .join("")
      .toLocaleUpperCase("es");
  }
  function avatar(name) {
    return el("span", "initial-avatar", initials(name));
  }
  document
    .querySelectorAll("[data-icon]")
    .forEach((e) => e.replaceWith(icon(e.dataset.icon)));
  let timer;
  function notify(text) {
    $("toast").textContent = text;
    $("toast").hidden = false;
    clearTimeout(timer);
    timer = setTimeout(() => ($("toast").hidden = true), 4500);
  }
  let session = null,
    csrf = "",
    authRegister = false,
    detailSequence = 0;
  let db = {
    profile: null,
    posts: [],
    communities: [],
    saved: [],
    reports: [],
  };
  const CATEGORY_API = {
    sport: "Deportes",
    outdoor: "Aire libre",
    culture: "Cultura",
    local: "Ferias y Comunidad",
  };
  const CATEGORY_UI = Object.fromEntries(
    Object.entries(CATEGORY_API).map(([a, b]) => [b, a]),
  );
  async function api(url, options = {}) {
    const headers = { ...options.headers };
    if (options.body && !(options.body instanceof FormData))
      headers["Content-Type"] = "application/json";
    if (options.method && options.method !== "GET") {
      if (!csrf) {
        const r = await fetch("/api/csrf/", { credentials: "same-origin" });
        csrf = (await r.json()).csrfToken;
      }
      headers["X-CSRFToken"] = csrf;
    }
    const response = await fetch(url, {
      credentials: "same-origin",
      ...options,
      headers,
    });
    const data = await response.json().catch(() => ({}));
    if (!response.ok)
      throw new Error(
        data.error || "No se pudo completar la operación. Vuelve a intentarlo.",
      );
    return data;
  }
  const json = (method, data) => ({ method, body: JSON.stringify(data) });
  function applySession(data) {
    session = data.authenticated ? data : null;
    db.profile = session
      ? {
          name: session.display_name || session.username,
          bio: session.bio || "",
          username: session.username,
          id: session.user_id,
        }
      : null;
  }
  function mapPost(a) {
    return {
      id: String(a.id),
      title: a.title,
      short: a.title.slice(0, 28),
      description: a.description,
      category: CATEGORY_UI[a.category] || "local",
      community: a.community_id ? String(a.community_id) : null,
      city: a.zone === "puerto-varas" ? "varas" : "montt",
      lat: a.lat,
      lng: a.lng,
      place:
        a.place ||
        (a.zone === "puerto-varas" ? "Puerto Varas" : "Puerto Montt"),
      kind: a.kind || "event",
      allYear: a.all_year,
      pace: a.pace || "calm",
      date: a.date || null,
      schedule: a.schedule,
      image: a.image_url || null,
      author: a.author_name || a.author || "Comunidad",
      owner: session && a.author_id === session.user_id ? "local" : null,
      canEdit: a.can_edit,
      featured: a.featured,
      status: a.status,
      example: a.example,
      comments: [],
      commentsCount: a.comments_count,
      created: Date.parse(a.created_at) || 0,
    };
  }
  function mapCommunity(c) {
    return {
      id: String(c.id),
      name: c.name,
      description: c.description,
      category: CATEGORY_UI[c.category] || "local",
      status: c.approved ? "published" : c.rejected ? "rejected" : "pending",
      owner: session && c.author_id === session.user_id ? "local" : null,
      postsCount: c.posts_count,
    };
  }
  async function loadData() {
    const [posts, groups, saved, reports] = await Promise.all([
      api("/api/activities/"),
      api("/api/communities/"),
      session ? api("/api/saved/") : Promise.resolve({ saved: [] }),
      session?.is_admin
        ? api("/api/reports/")
        : Promise.resolve({ reports: [] }),
    ]);
    db.posts = posts.activities.map(mapPost);
    db.communities = groups.communities.map(mapCommunity);
    db.saved = saved.saved.map(String);
    db.reports = reports.reports.map((r) => ({
      ...r,
      id: String(r.id),
      post: String(r.post_id),
    }));
    render();
  }
  function openAuth() {
    authRegister = false;
    updateAuthForm();
    $("auth-error").textContent = "";
    if (!$("auth-dialog").open) $("auth-dialog").showModal();
  }
  function updateAuthForm() {
    $("auth-title").textContent = authRegister
      ? "Crear una cuenta"
      : "Iniciar sesión";
    $("auth-submit").textContent = authRegister
      ? "Crear cuenta"
      : "Iniciar sesión";
    $("auth-toggle").textContent = authRegister
      ? "Ya tengo cuenta. Iniciar sesión"
      : "¿No tienes cuenta? Crear una cuenta";
    $("auth-password").autocomplete = authRegister
      ? "new-password"
      : "current-password";
    $("auth-description").textContent = authRegister
      ? "Elige un usuario y una contraseña de al menos 8 caracteres que no sea común."
      : "Tu cuenta para publicar, guardar y conversar en Panorama.";
  }
  let view = "explore",
    tab = "posts",
    communityId = null,
    detailId = null,
    opener = null,
    picking = false,
    postImage = null,
    imageFile = null,
    removedImage = false,
    afterProfile = null,
    reviewTab = "posts",
    reportId = null;
  const filters = {
    city: "all",
    category: "all",
    date: "all",
    pace: "all",
    scope: "all",
    radius: 0,
    area: false,
  };
  let map,
    layer,
    markers = new Map(),
    mapRows = [],
    silentMap = false;
  function cityLabel(city) {
    return city === "varas" ? "Puerto Varas" : "Puerto Montt";
  }
  function groupFor(post) {
    return db.communities.find((c) => c.id === post.community);
  }
  function visible(post) {
    return post.status === "published" || post.owner === "local";
  }
  function schedule(post) {
    if (post.kind === "place" || post.allYear)
      return post.schedule || "Lugar de encuentro";
    if (!post.date) return "Fecha por conversar";
    const d = new Date(post.date),
      today = new Date();
    const day =
      d.toDateString() === today.toDateString()
        ? "Hoy"
        : new Intl.DateTimeFormat("es-CL", {
            weekday: "short",
            day: "numeric",
            month: "short",
          }).format(d);
    return (
      day +
      " · " +
      new Intl.DateTimeFormat("es-CL", {
        hour: "2-digit",
        minute: "2-digit",
        hourCycle: "h23",
      }).format(d)
    );
  }
  function distance(lat, lng) {
    const r = (x) => (x * Math.PI) / 180,
      a =
        Math.sin(r(lat + 41.4718) / 2) ** 2 +
        Math.cos(r(-41.4718)) *
          Math.cos(r(lat)) *
          Math.sin(r(lng + 72.9369) / 2) ** 2;
    return 6371 * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  }
  function matches(p) {
    if (!visible(p)) return false;
    if (view === "saved" && !db.saved.includes(p.id)) return false;
    if (view === "mine" && p.owner !== "local") return false;
    if (communityId && p.community !== communityId) return false;
    if (
      (filters.city !== "all" && p.city !== filters.city) ||
      (filters.category !== "all" && p.category !== filters.category) ||
      (filters.pace !== "all" && p.pace !== filters.pace)
    )
      return false;
    if (
      (filters.scope === "independent" && p.community) ||
      (filters.scope === "community" && !p.community)
    )
      return false;
    const q = $("search").value.trim().toLocaleLowerCase("es");
    if (
      q &&
      ![
        p.title,
        p.description,
        p.place,
        cityLabel(p.city),
        groupFor(p)?.name || "",
      ]
        .join(" ")
        .toLocaleLowerCase("es")
        .includes(q)
    )
      return false;
    if (filters.radius && distance(p.lat, p.lng) > filters.radius) return false;
    if (filters.area && map && !map.getBounds().contains([p.lat, p.lng]))
      return false;
    if (filters.date === "permanent" && p.kind !== "place") return false;
    if (filters.date === "today" || filters.date === "weekend") {
      if (!p.date || p.kind === "place") return false;
      const start = new Date();
      start.setHours(0, 0, 0, 0);
      const end = new Date(start);
      if (filters.date === "weekend") {
        start.setDate(
          start.getDate() +
            (start.getDay() === 0 ? 0 : (6 - start.getDay() + 7) % 7),
        );
        end.setTime(start.getTime());
        if (start.getDay() === 6) end.setDate(end.getDate() + 1);
      }
      end.setHours(23, 59, 59, 999);
      const d = new Date(p.date);
      if (d < start || d > end) return false;
    }
    return true;
  }
  function filtered() {
    const rows = db.posts.filter(matches),
      sort = $("sort").value;
    return rows.sort(
      sort === "recent"
        ? (a, b) => (b.created || 0) - (a.created || 0)
        : sort === "comments"
          ? (a, b) => b.commentsCount - a.commentsCount
          : (a, b) =>
              Number(b.featured) - Number(a.featured) ||
              (b.created || 0) - (a.created || 0),
    );
  }
  function categoryIcon(cat) {
    return CATEGORIES[cat]?.icon || "pin";
  }
  function initMap() {
    if (!window.L) {
      const e = el("div", "map-error");
      e.append(
        el("h2", "", "El mapa necesita conexión"),
        el(
          "p",
          "",
          "Puedes seguir usando las publicaciones y comunidades. Conéctate a internet y vuelve a recargar la página.",
        ),
      );
      $("map").append(e);
      return;
    }
    map = L.map("map", { zoomControl: false, scrollWheelZoom: true }).setView(
      [-41.393, -72.95],
      11,
    );
    L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
      maxZoom: 19,
      attribution:
        '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
    }).addTo(map);
    L.control.zoom({ position: "bottomright" }).addTo(map);
    L.control.scale({ imperial: false, position: "bottomright" }).addTo(map);
    layer = L.layerGroup().addTo(map);
    if (matchMedia("(min-width:681px)").matches)
      map.panBy([-$("feed").getBoundingClientRect().width / 2, 0], {
        animate: false,
      });
    map.on("zoomend", drawMarkers);
    map.on("moveend", () => {
      if (!silentMap && !picking) $("search-area").hidden = false;
    });
    map.on("click", (e) => {
      if (!picking) return;
      $("post-lat").value = e.latlng.lat.toFixed(5);
      $("post-lng").value = e.latlng.lng.toFixed(5);
      updateLocationText();
      endPicking();
    });
  }
  function drawMarkers() {
    if (!map) return;
    layer.clearLayers();
    markers.clear();
    const near = map.getZoom() >= 15;
    $("zoom-caption").textContent = near
      ? "Ahora ves también las publicaciones sin destacar"
      : "Acerca el mapa para ver más publicaciones";
    const clusters = [];
    mapRows
      .filter((p) => p.status === "published" && (p.featured || near))
      .forEach((p) => {
        const point = map.latLngToContainerPoint([p.lat, p.lng]);
        const cluster =
          map.getZoom() < 16
            ? clusters.find((c) => c.point.distanceTo(point) < 52)
            : null;
        if (cluster) cluster.posts.push(p);
        else clusters.push({ point, posts: [p] });
      });
    clusters.forEach((c) => {
      const p = c.posts[0];
      if (c.posts.length > 1) {
        const face = el("span", "pin-cluster", c.posts.length);
        const m = L.marker([p.lat, p.lng], {
          title: c.posts.length + " publicaciones, acercar",
          icon: L.divIcon({
            className: "map-pin",
            html: face.outerHTML,
            iconSize: [36, 36],
            iconAnchor: [18, 18],
          }),
        }).addTo(layer);
        m.on("click", () =>
          map.fitBounds(
            c.posts.map((p) => [p.lat, p.lng]),
            { padding: [80, 80], maxZoom: 17 },
          ),
        );
        return;
      }
      const face = el("span", p.featured ? "pin-featured" : "pin-compact");
      if (p.featured) {
        const symbol = el("span", "pin-symbol");
        symbol.append(icon(categoryIcon(p.category)));
        face.append(
          symbol,
          document.createTextNode(p.short || p.title.slice(0, 28)),
        );
      } else face.append(icon(categoryIcon(p.category)));
      const m = L.marker([p.lat, p.lng], {
        title: p.title,
        alt: p.title,
        icon: L.divIcon({
          className: "map-pin",
          html: face.outerHTML,
          iconSize: p.featured ? [174, 36] : [28, 28],
          iconAnchor: p.featured ? [16, 18] : [14, 14],
        }),
      }).addTo(layer);
      m.on("click", () => openDetail(p.id));
      m.bindTooltip(p.title, { direction: "top", offset: [0, -20] });
      markers.set(p.id, m);
    });
    highlight(detailId);
  }
  function highlight(id) {
    markers.forEach((m, key) => {
      m.getElement()?.firstElementChild?.classList.toggle(
        "selected",
        key === id,
      );
      m.setZIndexOffset(key === id ? 1000 : 0);
    });
  }
  function focusMap(p) {
    if (!map) {
      notify("Conéctate a internet para abrir el mapa.");
      return;
    }
    silentMap = true;
    map.setView([p.lat, p.lng], p.featured ? 14 : 16, { animate: false });
    if (matchMedia("(min-width:681px)").matches)
      map.panBy([-$("feed").getBoundingClientRect().width / 2, 0], {
        animate: false,
      });
    else map.panBy([0, Math.round(map.getSize().y * 0.2)], { animate: false });
    silentMap = false;
    highlight(p.id);
  }
  function fitMap() {
    if (!map) return;
    const rows = mapRows.filter((p) => p.status === "published");
    if (!rows.length) {
      notify("No hay publicaciones publicadas con estos filtros.");
      return;
    }
    silentMap = true;
    const desktop = matchMedia("(min-width:681px)").matches;
    map.fitBounds(
      rows.map((p) => [p.lat, p.lng]),
      {
        paddingTopLeft: desktop
          ? [$("feed").getBoundingClientRect().width + 72, 108]
          : [36, 100],
        paddingBottomRight: desktop
          ? [88, 90]
          : [36, Math.round(map.getSize().y * 0.55)],
        maxZoom: 14,
        animate: false,
      },
    );
    silentMap = false;
    $("search-area").hidden = true;
  }
  function footnote(target) {
    const examples = db.posts.some((p) => p.example);
    if (examples)
      target.append(
        el(
          "p",
          "demo-footnote",
          "Los ejemplos identificados como tales no anuncian actividades reales.",
        ),
      );
  }
  function empty(target, title, text) {
    const e = el("div", "empty");
    e.append(el("h3", "", title), el("p", "", text));
    target.append(e);
    return e;
  }
  function postMeta(p) {
    const meta = el("div", "post-meta");
    meta.append(mark(p.category));
    const group = groupFor(p);
    if (group)
      meta.append(
        btn("p/" + group.name, null, "community-link", () =>
          enterCommunity(group.id),
        ),
      );
    else meta.append(el("span", "", "Publicación independiente"));
    return meta;
  }
  function postCard(p) {
    const card = el("article", "post");
    card.dataset.postId = p.id;
    card.classList.toggle("selected", detailId === p.id);
    const meta = postMeta(p);
    const save = btn("", "save", "post-save", () => toggleSaved(p));
    save.setAttribute(
      "aria-label",
      (db.saved.includes(p.id) ? "Quitar de guardados " : "Guardar ") + p.title,
    );
    save.setAttribute("aria-pressed", String(db.saved.includes(p.id)));
    meta.append(save);
    const h = el("h2");
    h.append(btn(p.title, null, "post-title", () => openDetail(p.id)));
    const sub = el("div", "post-subline");
    sub.append(el("span", "", CATEGORIES[p.category]?.name || "Comunidad"));
    if (p.featured) {
      sub.append(el("span", "separator"));
      const star = el("span", "featured-tag");
      star.append(icon("star"), document.createTextNode("Destacada"));
      sub.append(star);
    }
    if (p.example) sub.append(el("span", "", "Ejemplo"));
    if (p.status !== "published")
      sub.append(
        el(
          "span",
          "state-label",
          p.status === "pending" ? "En revisión" : "No publicada",
        ),
      );
    card.append(
      meta,
      h,
      sub,
      fact("pin", p.place || cityLabel(p.city), "post-location"),
      fact("clock", schedule(p), "post-date"),
    );
    if (p.image) {
      const img = el("img", "post-photo");
      img.src = p.image;
      img.alt = "Imagen adjuntada por " + p.author;
      img.loading = "lazy";
      card.append(img);
    }
    card.append(el("p", "post-description", p.description));
    const actions = el("div", "post-actions");
    actions.append(
      btn(
        p.commentsCount === 1
          ? "1 comentario"
          : p.commentsCount + " comentarios",
        "chat",
        "",
        () => openDetail(p.id, true),
      ),
      btn("Ver lugar", "pin", "", () => {
        closeDetail();
        focusMap(p);
      }),
      btn("", "share", "share", () => sharePost(p)),
    );
    actions.lastChild.setAttribute("aria-label", "Compartir " + p.title);
    card.append(actions);
    card.onmouseenter = () => highlight(p.id);
    card.onmouseleave = () => highlight(detailId);
    card.onfocusin = () => highlight(p.id);
    return card;
  }
  function toggleSaved(p) {
    withProfile(async () => {
      try {
        const saved = db.saved.includes(p.id);
        await api("/api/saved/" + p.id + "/", {
          method: saved ? "DELETE" : "POST",
        });
        await loadData();
        if (detailId === p.id) await openDetail(p.id);
        notify(
          saved ? "Publicación quitada de guardados" : "Publicación guardada",
        );
      } catch (e) {
        notify(e.message);
      }
    });
  }
  function render() {
    const rows = filtered(),
      group = db.communities.find((c) => c.id === communityId);
    $("feed-title").textContent = group
      ? group.name
      : view === "saved"
        ? "Tus guardados"
        : view === "mine"
          ? "Tus publicaciones"
          : tab === "communities"
            ? "Encuentra tu comunidad"
            : "Explora cerca de ti";
    $("region-line").replaceChildren(
      icon("pin"),
      document.createTextNode(
        group
          ? "Comunidad de " + CATEGORIES[group.category].name
          : filters.city === "all"
            ? "Puerto Montt y Puerto Varas"
            : cityLabel(filters.city),
      ),
    );
    document.querySelectorAll("[data-nav]").forEach((b) => {
      const name = b.dataset.nav;
      const selected =
        name ===
        (tab === "communities"
          ? "communities"
          : view === "saved"
            ? "saved"
            : "explore");
      if (selected) b.setAttribute("aria-current", "page");
      else b.removeAttribute("aria-current");
    });
    $("tab-posts").tabIndex = tab === "posts" ? 0 : -1;
    $("tab-communities").tabIndex = tab === "communities" ? 0 : -1;
    $("tab-posts").setAttribute("aria-selected", String(tab === "posts"));
    $("tab-communities").setAttribute(
      "aria-selected",
      String(tab === "communities"),
    );
    $("sort").hidden = tab === "communities";
    $("topic-chips").hidden = tab !== "communities";
    const count = Object.entries(filters).filter(([k, v]) =>
      k === "area" ? v : k === "radius" ? v > 0 : v !== "all",
    ).length;
    $("filter-count").hidden = !count;
    $("filter-count").textContent = count;
    $("clear-filters").hidden = !count;
    $("sort").hidden = tab === "communities" || Boolean(count);
    $("filter-open").classList.toggle("active", Boolean(count));
    ["city", "category", "date", "pace"].forEach((k) => {
      $("filter-" + k).value = filters[k];
      $("filter-" + k).classList.toggle("active", filters[k] !== "all");
    });
    $("filters-apply").textContent = "Ver " + rows.length + " publicaciones";
    mapRows = rows;
    drawMarkers();
    const body = $("feed-body");
    body.replaceChildren();
    if (tab === "communities") renderCommunities(body);
    else {
      if (group) {
        const info = el("div", "community-summary");
        info.append(el("p", "", group.description));
        const footer = el("footer");
        footer.append(
          btn("Publicar aquí", "plus", "primary small", () =>
            withProfile(() => openComposer()),
          ),
          btn("Volver a explorar", null, "text-button", () =>
            navigate("explore"),
          ),
        );
        info.append(
          footer,
          el(
            "p",
            "community-rules",
            "Comparte actividades de este interés y conversa con respeto",
          ),
        );
        body.append(info);
      }
      $("result-count").textContent =
        rows.length +
        " " +
        (rows.length === 1 ? "publicación" : "publicaciones");
      if (!rows.length) {
        const e = empty(
          body,
          view === "saved"
            ? "Tus próximos panoramas, aquí"
            : "No hay publicaciones por aquí",
          view === "saved"
            ? "Guarda una publicación para volver a encontrarla."
            : "Prueba otro interés o limpia los filtros. También puedes iniciar una conversación.",
        );
        e.append(
          btn(
            view === "saved" ? "Explorar publicaciones" : "Crear publicación",
            view === "saved" ? "map" : "plus",
            "small",
            () =>
              view === "saved"
                ? navigate("explore")
                : withProfile(() => openComposer()),
          ),
        );
      }
      rows.forEach((p) => body.append(postCard(p)));
    }
    footnote(body);
    updateProfileButton();
  }
  function resetFilters() {
    Object.assign(filters, {
      city: "all",
      category: "all",
      date: "all",
      pace: "all",
      scope: "all",
      radius: 0,
      area: false,
    });
    $("search").value = "";
    $("search-area").hidden = true;
  }
  function navigate(next) {
    if (next === "profile") {
      openProfile();
      return;
    }
    closeDetail();
    communityId = null;
    view = next === "saved" ? "saved" : "explore";
    tab = next === "communities" ? "communities" : "posts";
    resetFilters();
    document.body.classList.remove("feed-collapsed");
    syncCollapse();
    render();
    $("feed-body").scrollTop = 0;
  }
  function enterCommunity(id) {
    closeDetail();
    view = "explore";
    tab = "posts";
    communityId = id;
    resetFilters();
    document.body.classList.remove("feed-collapsed");
    syncCollapse();
    render();
    $("feed-body").scrollTop = 0;
  }
  function renderCommunities(body) {
    const chips = $("topic-chips");
    chips.replaceChildren();
    [
      ["all", "Todos"],
      ...Object.entries(CATEGORIES).map(([id, c]) => [id, c.name]),
    ].forEach(([id, name]) => {
      const b = btn(name, null, "", () => {
        filters.category = id;
        render();
      });
      b.setAttribute("aria-pressed", String(filters.category === id));
      chips.append(b);
    });
    body.append(
      btn("Crear una comunidad", "plus", "community-new", () =>
        withProfile(() => $("community-dialog").showModal()),
      ),
    );
    const q = $("search").value.trim().toLocaleLowerCase("es");
    const groups = db.communities.filter(
      (c) =>
        (c.status === "published" || c.owner === "local") &&
        (filters.category === "all" || c.category === filters.category) &&
        (!q ||
          [c.name, c.description]
            .join(" ")
            .toLocaleLowerCase("es")
            .includes(q)),
    );
    $("result-count").textContent = groups.length + " comunidades";
    groups.forEach((c) => {
      const card = el("article", "community-card"),
        head = el("div", "community-card-head");
      head.append(mark(c.category), el("h2", "", "p/" + c.name));
      card.append(head, el("p", "", c.description));
      const count = db.posts.filter(
          (p) => p.community === c.id && visible(p),
        ).length,
        footer = el("footer");
      footer.append(
        el(
          "span",
          "",
          count + " " + (count === 1 ? "publicación" : "publicaciones"),
        ),
      );
      if (c.status === "published")
        footer.append(btn("Entrar", null, "small", () => enterCommunity(c.id)));
      else
        footer.append(
          el(
            "span",
            "state-label",
            c.status === "pending" ? "En revisión" : "No publicada",
          ),
        );
      card.append(footer);
      body.append(card);
    });
    if (!groups.length)
      empty(
        body,
        "Aquí puede comenzar una comunidad",
        "Propón un espacio para ese interés que todavía no encuentras.",
      );
  }
  function closeDetail() {
    detailSequence++;
    detailId = null;
    $("detail").hidden = true;
    document
      .querySelectorAll(".post.selected")
      .forEach((c) => c.classList.remove("selected"));
    highlight(null);
    opener?.focus({ preventScroll: true });
  }
  async function openDetail(id, scrollComments = false) {
    const p = db.posts.find((p) => p.id === id && visible(p));
    if (!p) return;
    opener = document.activeElement;
    detailId = id;
    const seq = ++detailSequence;
    $("detail").hidden = false;
    $("detail-body").replaceChildren(
      el("p", "notice", "Cargando conversación…"),
    );
    render();
    try {
      const data = await api("/api/activities/" + id + "/comments/");
      if (seq !== detailSequence || detailId !== id) return;
      p.comments = data.comments.map((c) => ({
        id: String(c.id),
        author: c.display_name || c.author,
        text: c.text,
        date: c.created_at,
        owner: c.can_delete ? "local" : null,
      }));
      p.commentsCount = p.comments.length;
      renderDetail(p);
      $("detail-title").focus({ preventScroll: true });
      if (scrollComments)
        $("conversation-heading").scrollIntoView({ block: "start" });
    } catch (e) {
      if (seq !== detailSequence) return;
      const body = $("detail-body");
      body.replaceChildren(
        el("p", "notice", e.message),
        btn("Reintentar", null, "", () => openDetail(id, scrollComments)),
      );
    }
  }
  function renderDetail(p) {
    const body = $("detail-body");
    body.replaceChildren();
    body.append(postMeta(p));
    const title = el("h2", "", p.title);
    title.id = "detail-title";
    title.tabIndex = -1;
    body.append(
      title,
      fact("pin", p.place || cityLabel(p.city), "post-location"),
      fact("clock", schedule(p), "post-date"),
      el("p", "detail-author", "Publicado por " + p.author),
    );
    if (p.status !== "published")
      body.append(
        el(
          "p",
          "notice",
          p.status === "pending"
            ? "En revisión. Solo tú y el equipo moderador pueden ver esta propuesta."
            : "Esta propuesta no está publicada. Puedes editarla y enviarla otra vez.",
        ),
      );
    if (p.image) {
      const img = el("img", "post-photo");
      img.src = p.image;
      img.alt = "Imagen adjuntada por " + p.author;
      body.append(img);
    }
    body.append(el("p", "detail-description", p.description));
    const tools = el("div", "detail-tools");
    tools.append(
      btn(db.saved.includes(p.id) ? "Guardado" : "Guardar", "save", "", () => {
        toggleSaved(p);
        renderDetail(p);
      }),
      btn("Compartir", "share", "", () => sharePost(p)),
      btn("Reportar", "flag", "quiet", () => {
        reportId = p.id;
        $("report-form").reset();
        $("report-dialog").showModal();
      }),
    );
    if (p.owner === "local" || p.canEdit)
      tools.append(
        btn("Editar", "edit", "quiet", () =>
          withProfile(() => openComposer(p)),
        ),
      );
    if (p.canEdit)
      tools.append(
        btn("Eliminar", null, "quiet danger", async () => {
          if (!confirm("¿Eliminar esta publicación y sus comentarios?")) return;
          try {
            await api("/api/activities/" + p.id + "/", { method: "DELETE" });
            closeDetail();
            await loadData();
            notify("Publicación eliminada");
          } catch (e) {
            notify(e.message);
          }
        }),
      );
    body.append(tools);
    const section = el("section", "conversation"),
      heading = el("h3", "", "Conversación");
    heading.id = "conversation-heading";
    heading.append(el("span", "conversation-count", p.commentsCount));
    section.append(heading);
    if (p.example)
      section.append(
        el(
          "p",
          "conversation-caption",
          "Publicación y conversación de ejemplo",
        ),
      );
    const comments = el("div", "comments-list");
    if (!p.commentsCount)
      comments.append(
        el(
          "p",
          "comment-empty",
          "Todavía no hay comentarios. Puedes empezar con una pregunta.",
        ),
      );
    p.comments.forEach((c) => {
      const article = el("article", "comment");
      article.append(avatar(c.author));
      const text = el("div"),
        head = el("div", "comment-heading");
      head.append(el("strong", "", c.author));
      const time = el(
        "time",
        "",
        new Intl.DateTimeFormat("es-CL", {
          day: "numeric",
          month: "short",
        }).format(new Date(c.date)),
      );
      time.dateTime = c.date;
      head.append(time);
      text.append(head, el("p", "", c.text));
      if (c.owner === "local")
        text.append(
          btn("Eliminar", null, "text-button danger", () => {
            if (!confirm("¿Eliminar este comentario?")) return;
            api("/api/comments/" + c.id + "/", { method: "DELETE" })
              .then(async () => {
                await loadData();
                await openDetail(p.id, true);
              })
              .catch((e) => notify(e.message));
          }),
        );
      article.append(text);
      comments.append(article);
    });
    section.append(comments);
    const form = el("form", "comment-form"),
      field = el("textarea");
    field.id = "comment-input";
    field.required = true;
    field.maxLength = 2000;
    field.placeholder = db.profile
      ? "Pregunta o comparte lo que sabes"
      : "Escribe una pregunta para la comunidad";
    field.setAttribute("aria-label", "Comentario");
    const submit = el(
      "button",
      "primary",
      db.profile ? "Comentar" : "Iniciar sesión y comentar",
    );
    submit.type = "submit";
    form.append(field, submit);
    form.onsubmit = (e) => {
      e.preventDefault();
      const text = field.value.trim();
      if (!text) return;
      const send = async () => {
        submit.disabled = true;
        try {
          await api(
            "/api/activities/" + p.id + "/comments/",
            json("POST", { text }),
          );
          await loadData();
          await openDetail(p.id, true);
          $("comment-input")?.focus({ preventScroll: true });
          notify("Comentario publicado");
        } catch (e) {
          notify(e.message);
          submit.disabled = false;
        }
      };
      withProfile(send);
    };
    section.append(form);
    body.append(section);
  }
  function sharePost(p) {
    const url = new URL(location.href);
    url.hash = "post=" + encodeURIComponent(p.id);
    $("share-url").value = url.toString();
    $("share-dialog").showModal();
  }
  $("share-copy").onclick = async () => {
    try {
      await navigator.clipboard.writeText($("share-url").value);
      notify("Enlace copiado");
    } catch {
      $("share-url").select();
      notify("Selecciona y copia el enlace");
    }
  };
  function withProfile(fn) {
    if (session) {
      fn();
      return;
    }
    afterProfile = fn;
    openAuth();
  }
  function updateProfileButton() {
    const b = $("open-profile");
    b.replaceChildren(db.profile ? avatar(db.profile.name) : icon("user"));
    b.setAttribute(
      "aria-label",
      db.profile ? "Perfil de " + db.profile.name : "Abrir tu perfil",
    );
  }
  function editProfile() {
    if ($("profile-dialog").open) $("profile-dialog").close();
    $("profile-name").value = db.profile?.name || "";
    $("profile-bio").value = db.profile?.bio || "";
    $("profile-error").textContent = "";
    $("profile-edit-dialog").showModal();
  }
  $("profile-form").onsubmit = async (e) => {
    e.preventDefault();
    $("profile-error").textContent = "";
    const send = e.submitter;
    send.disabled = true;
    try {
      applySession(
        await api(
          "/api/profile/",
          json("PATCH", {
            name: $("profile-name").value.trim(),
            bio: $("profile-bio").value.trim(),
          }),
        ),
      );
      await loadData();
      $("profile-edit-dialog").close();
      openProfile();
    } catch (err) {
      $("profile-error").textContent = err.message;
    } finally {
      send.disabled = false;
    }
  };
  $("profile-edit-dialog").addEventListener(
    "cancel",
    () => (afterProfile = null),
  );
  function openProfile() {
    if (!db.profile) {
      afterProfile = () => openProfile();
      openAuth();
      return;
    }
    const target = $("profile-content");
    target.replaceChildren();
    const top = el("div", "profile-top"),
      text = el("div");
    text.append(
      el("h2", "", db.profile.name),
      el("p", "", db.profile.bio || "Explorando Puerto Montt y Puerto Varas"),
    );
    top.append(avatar(db.profile.name), text);
    const stats = el("div", "profile-stats");
    [
      [db.posts.filter((p) => p.owner === "local").length, "Publicaciones"],
      [db.saved.length, "Guardados"],
      [db.communities.filter((c) => c.owner === "local").length, "Comunidades"],
    ].forEach(([n, label]) => {
      const e = el("span", "", label);
      e.prepend(el("strong", "", n));
      stats.append(e);
    });
    target.append(top, stats);
    const links = el("div", "profile-links");
    links.append(
      btn("Editar perfil", "edit", "quiet", editProfile),
      btn("Mis publicaciones", "chat", "quiet", () => {
        $("profile-dialog").close();
        navigate("explore");
        view = "mine";
        render();
      }),
      btn("Mis guardados", "save", "quiet", () => {
        $("profile-dialog").close();
        navigate("saved");
      }),
      ...(session.is_admin
        ? [
            btn("Revisar contenido", "shield", "quiet", () => {
              $("profile-dialog").close();
              reviewTab = "posts";
              renderReview();
              $("moderation-dialog").showModal();
            }),
          ]
        : []),
      btn("Cerrar sesión", "user", "quiet", logout),
    );
    target.append(
      links,
      el(
        "p",
        "notice",
        "Tu cuenta usa nombre de usuario y contraseña. La decisión sobre el RUT sigue pendiente.",
      ),
    );
    $("profile-dialog").showModal();
  }
  function uid(prefix) {
    return (
      prefix +
      "-" +
      (crypto.randomUUID
        ? crypto.randomUUID()
        : Date.now().toString(36) + Math.random().toString(36).slice(2))
    );
  }
  function openComposer(post = null) {
    imageSequence++;
    $("post-submit").disabled = false;
    $("post-form").reset();
    $("post-id").value = post?.id || "";
    $("post-error").textContent = "";
    $("post-dialog-title").textContent = post
      ? "Editar publicación"
      : "Crear publicación";
    imageFile = null;
    removedImage = false;
    postImage = post?.image || null;
    $("moderator-post-fields").hidden = !session?.is_admin;
    $("post-status").value = post?.status || "published";
    $("post-featured").checked = Boolean(post?.featured);
    $("post-submit").textContent = session?.is_admin
      ? "Guardar publicación"
      : "Enviar a revisión";
    $("post-community").replaceChildren(
      new Option("Publicación independiente", ""),
    );
    db.communities
      .filter((c) => c.status === "published")
      .forEach((c) =>
        $("post-community").append(new Option("p/" + c.name, c.id)),
      );
    $("post-community").value = post?.community || communityId || "";
    $("post-lat").value = post?.lat ?? "";
    $("post-lng").value = post?.lng ?? "";
    $("post-recurring").checked = Boolean(
      post?.allYear && post.kind !== "place",
    );
    if (post) {
      $("post-title-input").value = post.title;
      $("post-description").value = post.description;
      $("post-city").value = post.city;
      $("post-kind").value = post.kind;
      $("post-pace").value = post.pace;
      $("post-category").value = post.category;
      $("post-schedule").value = post.schedule || "";
      if (post.date) {
        const d = new Date(post.date);
        $("post-date").value = new Date(
          d.getTime() - d.getTimezoneOffset() * 60000,
        )
          .toISOString()
          .slice(0, 16);
      }
    }
    syncPostGroup();
    syncPostKind();
    updateImagePreview();
    updateLocationText();
    $("post-dialog").showModal();
  }
  function syncPostGroup() {
    const c = db.communities.find((c) => c.id === $("post-community").value);
    $("post-category").disabled = Boolean(c);
    if (c) $("post-category").value = c.category;
  }
  function syncPostKind() {
    const place = $("post-kind").value === "place",
      habitual = place || $("post-recurring").checked;
    $("post-recurring-label").hidden = place;
    $("post-date-label").hidden = habitual;
    $("post-date").required = !habitual;
    $("post-schedule-label").hidden = !habitual;
  }
  function updateLocationText() {
    $("post-location-text").textContent = $("post-lat").value
      ? Number($("post-lat").value).toFixed(4) +
        ", " +
        Number($("post-lng").value).toFixed(4)
      : "Elige el punto de encuentro";
  }
  function updateImagePreview() {
    $("post-image-preview").hidden = !postImage;
    $("remove-photo").hidden = !postImage;
    if (postImage) $("post-image-preview").src = postImage;
    else $("post-image-preview").removeAttribute("src");
  }
  let imageSequence = 0;
  $("post-image").onchange = async () => {
    const seq = ++imageSequence,
      file = $("post-image").files[0];
    if (!file) return;
    $("post-error").textContent = "";
    if (
      !["image/jpeg", "image/png", "image/webp"].includes(file.type) ||
      file.size > 5 * 1024 * 1024
    ) {
      $("post-error").textContent =
        "Usa una imagen JPG, PNG o WebP de hasta 5 MB";
      $("post-image").value = "";
      return;
    }
    $("post-submit").disabled = true;
    try {
      const url = URL.createObjectURL(file);
      try {
        const image = new Image();
        await new Promise((resolve, reject) => {
          image.onload = resolve;
          image.onerror = reject;
          image.src = url;
        });
        const scale = Math.min(
            1,
            1400 / Math.max(image.naturalWidth, image.naturalHeight),
          ),
          canvas = document.createElement("canvas");
        canvas.width = Math.round(image.naturalWidth * scale);
        canvas.height = Math.round(image.naturalHeight * scale);
        canvas
          .getContext("2d")
          .drawImage(image, 0, 0, canvas.width, canvas.height);
        if (seq === imageSequence) {
          imageFile = file;
          removedImage = false;
          postImage = canvas.toDataURL("image/jpeg", 0.82);
          updateImagePreview();
        }
      } finally {
        URL.revokeObjectURL(url);
      }
    } catch {
      $("post-error").textContent =
        "No pudimos abrir esta imagen. Prueba con otra.";
    } finally {
      if (seq === imageSequence) $("post-submit").disabled = false;
    }
  };
  $("remove-photo").onclick = () => {
    imageSequence++;
    imageFile = null;
    removedImage = true;
    postImage = null;
    $("post-image").value = "";
    $("post-submit").disabled = false;
    updateImagePreview();
  };
  $("post-community").onchange = syncPostGroup;
  $("post-kind").onchange = syncPostKind;
  $("post-recurring").onchange = syncPostKind;
  $("post-pick").onclick = () => {
    if (!map) {
      $("post-error").textContent =
        "Conéctate a internet para elegir una ubicación en el mapa";
      return;
    }
    picking = true;
    $("post-dialog").close();
    closeDetail();
    document.body.classList.add("picking");
    $("pick-message").hidden = false;
    map.invalidateSize();
  };
  function endPicking() {
    picking = false;
    document.body.classList.remove("picking");
    $("pick-message").hidden = true;
    $("post-dialog").showModal();
  }
  $("pick-cancel").onclick = endPicking;
  $("post-form").onsubmit = async (e) => {
    e.preventDefault();
    if (!$("post-lat").value || !$("post-lng").value) {
      $("post-error").textContent =
        "Elige primero el punto de encuentro en el mapa";
      return;
    }
    const send = $("post-submit");
    send.disabled = true;
    $("post-error").textContent = "";
    const id = $("post-id").value,
      kind = $("post-kind").value;
    const payload = {
      title: $("post-title-input").value.trim(),
      description: $("post-description").value.trim(),
      category: CATEGORY_API[$("post-category").value],
      community_id: $("post-community").value || null,
      zone: $("post-city").value === "varas" ? "puerto-varas" : "puerto-montt",
      lat: Number($("post-lat").value),
      lng: Number($("post-lng").value),
      place: cityLabel($("post-city").value),
      kind,
      all_year: kind === "place" || $("post-recurring").checked,
      pace: $("post-pace").value,
      date:
        kind === "event" && !$("post-recurring").checked
          ? new Date($("post-date").value).toISOString()
          : null,
      schedule:
        kind === "place" || $("post-recurring").checked
          ? $("post-schedule").value.trim()
          : "",
      remove_image: removedImage,
    };
    if (session.is_admin) {
      payload.featured = $("post-featured").checked;
      payload.status = $("post-status").value;
    }
    try {
      const data = await api(
        id ? "/api/activities/" + id + "/" : "/api/activities/",
        json(id ? "PATCH" : "POST", payload),
      );
      $("post-id").value = data.activity.id;
      if (imageFile) {
        const form = new FormData();
        form.append("image", imageFile);
        await api("/api/activities/" + data.activity.id + "/image/", {
          method: "POST",
          body: form,
        });
      }
      $("post-dialog").close();
      closeDetail();
      view = "mine";
      tab = "posts";
      communityId = null;
      resetFilters();
      await loadData();
      $("feed-body").scrollTop = 0;
      notify(
        session.is_admin
          ? "Publicación guardada"
          : "Propuesta enviada al equipo moderador",
      );
    } catch (err) {
      $("post-error").textContent =
        err.message +
        ($("post-id").value
          ? " El texto ya está guardado; puedes corregir el adjunto y volver a enviar."
          : "");
    } finally {
      send.disabled = false;
    }
  };
  $("community-form").onsubmit = async (e) => {
    e.preventDefault();
    const send = e.submitter;
    send.disabled = true;
    $("community-error").textContent = "";
    try {
      await api(
        "/api/communities/",
        json("POST", {
          name: $("community-name").value.trim(),
          category: CATEGORY_API[$("community-category").value],
          description: $("community-description").value.trim(),
        }),
      );
      $("community-dialog").close();
      $("community-form").reset();
      await loadData();
      navigate("communities");
      notify(
        session.is_admin ? "Comunidad creada" : "Comunidad enviada a revisión",
      );
    } catch (err) {
      $("community-error").textContent = err.message;
    } finally {
      send.disabled = false;
    }
  };
  function renderReview() {
    const target = $("moderation-content");
    target.replaceChildren();
    document
      .querySelectorAll("[data-review]")
      .forEach((b) =>
        b.setAttribute("aria-selected", String(b.dataset.review === reviewTab)),
      );
    if (reviewTab === "posts") {
      const rows = db.posts.filter((p) => p.status === "pending");
      if (!rows.length)
        empty(
          target,
          "No hay publicaciones pendientes",
          "Las propuestas nuevas aparecerán aquí para que puedas revisar el contenido.",
        );
      rows.forEach((p) => {
        const c = el("article", "community-card");
        c.append(
          el("h3", "", p.title),
          el("p", "", p.description),
          el(
            "p",
            "",
            cityLabel(p.city) +
              " · " +
              (groupFor(p)?.name || "Publicación independiente"),
          ),
        );
        if (p.image) {
          const img = el("img", "post-photo");
          img.src = p.image;
          img.alt = "Imagen de la propuesta";
          c.append(img);
        }
        const actions = el("div", "review-actions");
        [
          ["Publicar", false, "published"],
          ["Destacar y publicar", true, "published"],
          ["Rechazar", false, "rejected"],
        ].forEach(([label, feature, status]) =>
          actions.append(
            btn(
              label,
              status === "published" ? "check" : null,
              status === "published" ? "small primary" : "small quiet danger",
              () => {
                reviewAction(async () => {
                  await api(
                    "/api/activities/" + p.id + "/",
                    json("PATCH", { featured: feature, status }),
                  );
                  await loadData();
                  renderReview();
                  if (detailId === p.id) await openDetail(p.id);
                  notify(
                    status === "published"
                      ? "Publicación aprobada"
                      : "Propuesta rechazada",
                  );
                });
              },
            ),
          ),
        );
        c.append(actions);
        target.append(c);
      });
    } else if (reviewTab === "communities") {
      const rows = db.communities.filter((c) => c.status === "pending");
      if (!rows.length)
        empty(
          target,
          "No hay comunidades pendientes",
          "Las propuestas de comunidades se revisan aquí.",
        );
      rows.forEach((c) => {
        const card = el("article", "community-card");
        card.append(el("h3", "", c.name), el("p", "", c.description));
        const actions = el("div", "review-actions");
        actions.append(
          btn("Aprobar", "check", "primary small", () => {
            reviewAction(async () => {
              await api(
                "/api/communities/" + c.id + "/moderate/",
                json("POST", { approved: true }),
              );
              await loadData();
              renderReview();
              notify("Comunidad publicada");
            });
          }),
          btn("Rechazar", null, "quiet small danger", () => {
            reviewAction(async () => {
              await api(
                "/api/communities/" + c.id + "/moderate/",
                json("POST", { approved: false, rejected: true }),
              );
              await loadData();
              renderReview();
            });
          }),
        );
        card.append(actions);
        target.append(card);
      });
    } else {
      if (!db.reports.length)
        empty(
          target,
          "No hay reportes",
          "Puedes reportar contenido desde Reportar, dentro de una publicación.",
        );
      db.reports.forEach((r) => {
        const c = el("article", "community-card"),
          p = db.posts.find((p) => p.id === r.post);
        c.append(
          el("h3", "", p?.title || "Publicación eliminada"),
          el("p", "", r.reason),
          el("p", "", r.text || "Sin información adicional"),
        );
        const actions = el("div", "review-actions");
        actions.append(
          btn("Marcar como revisado", "check", "small", () => {
            reviewAction(async () => {
              await api(
                "/api/reports/" + r.id + "/",
                json("PATCH", { resolved: true }),
              );
              await loadData();
              renderReview();
              notify("Reporte revisado");
            });
          }),
        );
        if (p)
          actions.append(
            btn("Ocultar publicación", null, "small quiet danger", () => {
              reviewAction(async () => {
                await api(
                  "/api/activities/" + p.id + "/",
                  json("PATCH", { status: "rejected", featured: false }),
                );
                await api(
                  "/api/reports/" + r.id + "/",
                  json("PATCH", { resolved: true }),
                );
                await loadData();
                renderReview();
                if (detailId === p.id) closeDetail();
                notify("Publicación ocultada");
              });
            }),
          );
        c.append(actions);
        target.append(c);
      });
    }
  }
  async function reviewAction(fn) {
    try {
      await fn();
    } catch (e) {
      notify(e.message);
    }
  }
  $("report-form").onsubmit = async (e) => {
    e.preventDefault();
    const send = e.submitter;
    withProfile(async () => {
      send.disabled = true;
      try {
        await api(
          "/api/reports/",
          json("POST", {
            post_id: reportId,
            reason: $("report-reason").value,
            text: $("report-text").value.trim(),
          }),
        );
        $("report-dialog").close();
        notify("Reporte enviado al equipo moderador");
      } catch (err) {
        notify(err.message);
      } finally {
        send.disabled = false;
      }
    });
  };
  document.querySelectorAll("[data-review]").forEach(
    (b) =>
      (b.onclick = () => {
        reviewTab = b.dataset.review;
        renderReview();
      }),
  );
  const filterGroups = [
    [
      "city",
      "Ciudad",
      [
        ["all", "Ambas ciudades"],
        ["montt", "Puerto Montt"],
        ["varas", "Puerto Varas"],
      ],
    ],
    [
      "category",
      "Qué te interesa",
      [
        ["all", "Todos"],
        ...Object.entries(CATEGORIES).map(([id, c]) => [id, c.name]),
      ],
    ],
    [
      "date",
      "Cuándo",
      [
        ["all", "Cualquier fecha"],
        ["today", "Hoy"],
        ["weekend", "Este fin de semana"],
        ["permanent", "Lugares de encuentro"],
      ],
    ],
    [
      "pace",
      "A tu ritmo",
      [
        ["all", "Cualquier ritmo"],
        ["active", "Más movimiento"],
        ["calm", "Algo tranquilo"],
      ],
    ],
    [
      "scope",
      "Dónde se publica",
      [
        ["all", "Todas las publicaciones"],
        ["community", "En comunidades"],
        ["independent", "Independientes"],
      ],
    ],
  ];
  function renderFilterDialog() {
    const target = $("filter-sections");
    target.replaceChildren();
    filterGroups.forEach(([key, label, options]) => {
      const section = el("section", "filter-section");
      section.append(el("h3", "", label));
      const group = el("div", "filter-options");
      group.setAttribute("aria-label", label);
      options.forEach(([value, name]) => {
        const b = btn(name, null, "", () => {
          filters[key] = value;
          renderFilterDialog();
          render();
          $("filter-sections")
            .querySelector(
              '[data-filter-key=\"' +
                key +
                '\"][data-filter-value=\"' +
                value +
                '\"]',
            )
            ?.focus({ preventScroll: true });
        });
        b.dataset.filterKey = key;
        b.dataset.filterValue = value;
        b.setAttribute("aria-pressed", String(filters[key] === value));
        group.append(b);
      });
      section.append(group);
      target.append(section);
    });
    $("filter-radius").value = filters.radius;
    $("radius-output").textContent = filters.radius
      ? filters.radius + " km"
      : "Sin límite";
  }
  $("filter-open").onclick = () => {
    renderFilterDialog();
    $("filters-dialog").showModal();
  };
  $("filter-radius").oninput = () => {
    filters.radius = Number($("filter-radius").value);
    $("radius-output").textContent = filters.radius
      ? filters.radius + " km"
      : "Sin límite";
    render();
  };
  $("filters-reset").onclick = () => {
    resetFilters();
    renderFilterDialog();
    render();
  };
  $("filters-apply").onclick = () => $("filters-dialog").close();
  ["city", "category", "date", "pace"].forEach(
    (k) =>
      ($("filter-" + k).onchange = () => {
        filters[k] = $("filter-" + k).value;
        closeDetail();
        render();
      }),
  );
  $("clear-filters").onclick = () => {
    resetFilters();
    render();
  };
  $("search").oninput = () => {
    closeDetail();
    render();
  };
  $("sort").onchange = render;
  function syncCollapse() {
    const collapsed = document.body.classList.contains("feed-collapsed");
    $("feed-collapse").setAttribute("aria-expanded", String(!collapsed));
    $("feed-collapse").setAttribute(
      "aria-label",
      collapsed ? "Expandir publicaciones" : "Recoger publicaciones",
    );
  }
  $("feed-collapse").onclick = () => {
    document.body.classList.toggle("feed-collapsed");
    syncCollapse();
  };
  $("new-post").onclick = () => withProfile(() => openComposer());
  $("open-profile").onclick = openProfile;
  $("detail-close").onclick = closeDetail;
  $("detail-map").onclick = () => {
    const p = db.posts.find((p) => p.id === detailId);
    closeDetail();
    if (p) {
      if (matchMedia("(max-width:680px)").matches) {
        document.body.classList.add("feed-collapsed");
        syncCollapse();
      }
      focusMap(p);
    }
  };
  $("map-fit").onclick = fitMap;
  $("search-area").onclick = () => {
    filters.area = true;
    render();
    $("search-area").hidden = true;
  };
  $("map-style").onclick = () => {
    const on = $("map-style-menu").hidden;
    $("map-style-menu").hidden = !on;
    $("map-style").setAttribute("aria-expanded", String(on));
  };
  document.querySelectorAll("[data-map-style]").forEach(
    (b) =>
      (b.onclick = () => {
        const soft = b.dataset.mapStyle === "soft";
        document
          .querySelector(".leaflet-tile-pane")
          ?.style.setProperty(
            "filter",
            soft ? "saturate(.68) contrast(.96) brightness(1.035)" : "none",
          );
        document
          .querySelectorAll("[data-map-style]")
          .forEach((x) => x.setAttribute("aria-pressed", String(x === b)));
        $("map-style-menu").hidden = true;
        $("map-style").setAttribute("aria-expanded", "false");
      }),
  );
  document
    .querySelectorAll("[data-nav]")
    .forEach((b) => (b.onclick = () => navigate(b.dataset.nav)));
  document.querySelectorAll("[data-close]").forEach(
    (b) =>
      (b.onclick = () => {
        if (b.dataset.close === "profile-edit-dialog") afterProfile = null;
        $(b.dataset.close).close();
      }),
  );
  document.querySelector(".wordmark").onclick = (e) => {
    e.preventDefault();
    navigate("explore");
  };
  $("tab-posts").onclick = () => {
    tab = "posts";
    render();
  };
  $("tab-communities").onclick = () => navigate("communities");
  document.addEventListener("keydown", (e) => {
    if (
      e.key === "/" &&
      !/INPUT|TEXTAREA|SELECT/.test(document.activeElement.tagName) &&
      !document.querySelector("dialog[open]")
    ) {
      e.preventDefault();
      $("search").focus();
    }
    if (e.key === "Escape" && picking) {
      endPicking();
      return;
    }
    if (e.key === "Escape" && !document.querySelector("dialog[open]")) {
      if (detailId) closeDetail();
      $("map-style-menu").hidden = true;
      $("map-style").setAttribute("aria-expanded", "false");
    }
  });
  document.querySelector(".feed-tabs").addEventListener("keydown", (e) => {
    if (!["ArrowLeft", "ArrowRight"].includes(e.key)) return;
    e.preventDefault();
    if (tab === "posts") {
      navigate("communities");
      $("tab-communities").focus();
    } else {
      tab = "posts";
      render();
      $("tab-posts").focus();
    }
  });
  window.addEventListener("resize", () => map?.invalidateSize());

  $("auth-toggle").onclick = () => {
    authRegister = !authRegister;
    updateAuthForm();
    $("auth-error").textContent = "";
  };
  $("auth-form").onsubmit = async (e) => {
    e.preventDefault();
    $("auth-submit").disabled = true;
    $("auth-error").textContent = "";
    try {
      const data = await api(
        authRegister ? "/api/register/" : "/api/login/",
        json("POST", {
          username: $("auth-username").value.trim(),
          password: $("auth-password").value,
        }),
      );
      csrf = "";
      applySession(data);
      $("auth-form").reset();
      $("auth-dialog").close();
      await loadData();
      if (detailId) await openDetail(detailId);
      const next = afterProfile;
      afterProfile = null;
      if (next) await next();
    } catch (err) {
      $("auth-error").textContent = err.message;
    } finally {
      $("auth-submit").disabled = false;
    }
  };
  $("auth-dialog").addEventListener("cancel", () => (afterProfile = null));
  async function logout() {
    try {
      await api("/api/logout/", { method: "POST" });
      csrf = "";
      applySession({ authenticated: false });
      $("profile-dialog").close();
      closeDetail();
      navigate("explore");
      await loadData();
      notify("Sesión cerrada");
    } catch (e) {
      notify(e.message);
    }
  }
  async function start() {
    try {
      applySession(await api("/api/session/"));
      await loadData();
      if (location.hash.startsWith("#post=")) {
        const id = decodeURIComponent(location.hash.slice(6));
        if (db.posts.some((p) => p.id === id && visible(p)))
          await openDetail(id);
        else
          notify(
            "La publicación no está disponible o necesitas iniciar sesión",
          );
      }
    } catch (e) {
      $("result-count").textContent = "No se pudo conectar";
      $("feed-body").replaceChildren(
        el("p", "notice", e.message),
        btn("Reintentar", null, "", start),
      );
    }
  }

  initMap();
  start();
})();
