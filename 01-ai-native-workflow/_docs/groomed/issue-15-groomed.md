# Issue #15 — PWA — Web App Manifest and Service Worker (Groomed)

## Goal
Make the app installable on phones and desktops as a Progressive Web App.

---

## Dependencies

| Dependency | Status |
|---|---|
| #1 — Project setup (static files serving configured) | ✅ Done |
| #2 — User registration & login (base template exists) | ⬜ Not started |

> [!NOTE]
> This issue is **independent of all business logic** (Tasks 3–14). It can be implemented as soon as a base HTML template exists from #2. It does not need to wait for gamification or the board.

---

## Deliverables

### 1. `manifest.json`

Served as a static file at `static/chores/manifest.json` (or a dedicated URL).

Required fields:

```json
{
  "name": "Shared Household Chores",
  "short_name": "HouseChores",
  "start_url": "/",
  "display": "standalone",
  "theme_color": "#ffffff",
  "background_color": "#ffffff",
  "icons": [
    {
      "src": "/static/chores/icons/icon-192.png",
      "sizes": "192x192",
      "type": "image/png"
    },
    {
      "src": "/static/chores/icons/icon-512.png",
      "sizes": "512x512",
      "type": "image/png"
    }
  ]
}
```

> [!IMPORTANT]
> Chrome requires **at least one icon of 192×192** and one of **512×512** for the install prompt to appear. Placeholder PNG files must be committed to the repo.

### 2. Base Template Link Tag

In the base template `<head>`:

```html
<link rel="manifest" href="{% static 'chores/manifest.json' %}">
<meta name="theme-color" content="#ffffff">
```

### 3. Service Worker

A minimal service worker at `static/chores/sw.js` that caches the app shell on install:

```javascript
const CACHE_NAME = "household-chores-v1";
const SHELL_URLS = ["/", "/static/chores/manifest.json"];

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(SHELL_URLS))
  );
});

self.addEventListener("fetch", (event) => {
  event.respondWith(
    caches.match(event.request).then((cached) => cached || fetch(event.request))
  );
});
```

### 4. Service Worker Registration Script

In the base template (before `</body>`):

```html
<script>
  if ("serviceWorker" in navigator) {
    navigator.serviceWorker.register("{% static 'chores/sw.js' %}");
  }
</script>
```

---

## Acceptance Criteria

- [ ] `manifest.json` is served and accessible in the browser (no 404).
- [ ] Manifest includes: `name`, `short_name`, `start_url`, `display: "standalone"`, `theme_color`, `background_color`, and at least one 192×192 icon and one 512×512 icon.
- [ ] The `<link rel="manifest">` tag is present in the rendered HTML `<head>`.
- [ ] A service worker is registered via a `<script>` in the base template.
- [ ] The service worker caches the app shell on install.
- [ ] Chrome DevTools → Application → Manifest shows **no errors**.
- [ ] Chrome DevTools → Application → Manifest shows the **Install** prompt (or "Add to Home Screen" button).
- [ ] The home page loads when offline after first visit.

---

## Static Files Setup

Confirm `STATICFILES_DIRS` or `AppDirectoriesFinder` is configured in `settings.py` so static files in `chores/static/chores/` are found by `collectstatic`.

---

## Tests to Write

> [!NOTE]
> Most PWA behaviour (install prompt, offline mode) requires a real browser and cannot be tested with Django's test client. Focus automated tests on static file availability and template correctness.

| Test | Type |
|---|---|
| `manifest.json` is served (HTTP 200) | Integration |
| Manifest response has `Content-Type: application/json` | Integration |
| `<link rel="manifest">` tag is present in rendered HTML | Integration |
| `sw.js` is served (HTTP 200) | Integration |
| Service worker registration `<script>` is present in rendered HTML | Integration |

---

## Open Questions

1. Should the manifest be served as a Django view (so the `start_url` can be dynamic) or as a plain static file? Plain static file is simpler and sufficient.
2. What colours should `theme_color` and `background_color` be? Decide once a design system (`_docs/design-system.md`) exists. Placeholders are fine for now.
3. Should the service worker use a **network-first** or **cache-first** strategy? Cache-first (as shown above) satisfies "home page loads offline"; network-first is safer for dynamic content. For this scope, cache-first for the app shell only is appropriate.
4. What icons should be used? Placeholder solid-colour PNGs are acceptable for the homework; replace with real icons later.

---

## Out of Scope

- Push notifications.
- Background sync.
- Full offline support for authenticated pages (only the home page needs to load offline).
- App store submission.
