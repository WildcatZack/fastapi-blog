# Project Brief — Uniform Jinja2-First Blog + Admin with React Islands (Single Python Image behind NPM)

> Purpose: give you (and future you) a crisp, **no-code** blueprint to build and run a blog (SEO-strong) plus an admin/control panel (great UX) in **one Docker image** with **FastAPI + Jinja2** and **React islands** for interactivity. It assumes **Nginx Proxy Manager (NPM)** is a separate container handling TLS and public routing.

---

## North-Star Decisions (lock-ins)

- **Rendering model (everywhere):** Jinja2 templates (server-rendered HTML).
- **Interactivity:** React “islands” (small components) mounted into Jinja pages.
- **Runtime:** Single **Python** container (no Node server at runtime).
- **Edge:** TLS termination + routing via **NPM** (separate container).
- **Content updates:** DB-driven; **no rebuild** required to publish posts.
- **Realtime:** WebSockets endpoint available from day one.
- **Admin editor:** **WYSIWYG** (Quill/TipTap-style) as a React island.
- **MVP feeds:** **RSS = Yes**, **Sitemap = Defer** (add soon after MVP).
- **Design libs:** Keep lean; optionally allow **Google Fonts** and **Bootstrap** via CSP. (Tailwind is fine too, but to minimize moving parts, start without it and add later if needed.)

---

## High-Level Architecture

- **FastAPI app** (single image):
  - **Views (HTML):** `/`, `/posts`, `/posts/{slug}`, `/tags/{tag}`, `/admin/*`
  - **APIs (JSON):** `/api/posts`, `/api/media`, `/api/auth`, `/api/config`, `/api/health`
  - **WebSockets:** `/ws` (topics via query/path)
  - **Static:** `/static/*` (hashed JS/CSS/images), served by the app
- **Data store:** relational DB (posts, tags, authors, media, users, sessions)
- **NPM (separate):** TLS (Let’s Encrypt), proxy apex domain → app container, WS passthrough

---

## Routing Contract (uniform & future-proof)

- **Public pages (server-rendered HTML):**
  - `/` — blog home (latest posts)
  - `/posts` — index with pagination
  - `/posts/{slug}` — full article page with SEO/meta/OG
  - `/tags/{tag}` — tag listing
  - `/feed.xml` — **RSS** (MVP)
  - `/about`, `/contact` — simple pages (optional)
- **Admin pages (server-rendered HTML + islands):**
  - `/admin` — dashboard
  - `/admin/posts` — list/manage posts
  - `/admin/posts/new` — **WYSIWYG editor island**
  - `/admin/posts/{id}/edit` — editor island with existing content
  - `/admin/media`, `/admin/settings`
- **APIs (JSON):**
  - `/api/posts` (CRUD), `/api/media` (upload/list), `/api/auth` (login/session), `/api/config` (env-derived UI runtime), `/api/health`
- **Realtime:**
  - `/ws` — supports topics like `?topic=post:{id}`, `?topic=chat:admin`

---

## Folder Layout (basic text version)

backend/  
-- views/ (page handlers for Jinja templates)  
-- routers/ (REST APIs under /api/\*)  
-- templates/ (Jinja HTML for public + admin)  
-- services/ (DB/content/auth logic)  
-- ws/ (WebSocket handlers)

frontend/  
-- islands/ (React components for public pages)  
-- admin_islands/ (React components for admin pages)  
-- build/ (output: hashed JS/CSS bundles)

static/ (images, favicon, manifest, etc.)  
Dockerfile (multi-stage: Node build → Python runtime)  
compose.yml (app service only, NPM separate)  
docs/ (ops notes, CSP allow-list, release checklist)  
README.md

---

## Build & Runtime (single image)

- **Multi-stage build:**
  1. **Node builder:** compile React islands (public + admin) → hashed bundles
  2. **Python runtime:** install FastAPI app; copy bundles into `/app/static/assets/`
- **Serve paths:**
  - HTML from **Jinja2 templates**
  - Assets from `/static/assets/` (immutable hashed filenames)
  - APIs under `/api/*`
  - WS at `/ws`
- **Env/runtime config for islands:** expose `window.__APP_CONFIG__` via a tiny `/app-config.js` (or `/api/config`) so no rebuild per environment.

---

## Security & Headers

- **At NPM (edge):**
  - Let’s Encrypt, **Force SSL**, **Enable WebSockets**
  - Add **HSTS** when you’re confident: `max-age=31536000; includeSubDomains; preload`
- **At App (duplicate is fine):**
  - `X-Content-Type-Options: nosniff`
  - `Referrer-Policy: strict-origin-when-cross-origin` (or `same-origin`)
  - `X-Frame-Options: DENY` (or `SAMEORIGIN` if embedding admin)
  - `Permissions-Policy`: disable unused features (`camera=(), microphone=(), geolocation=()`…)
  - **CSP (phase-in)**
    - Phase 1 (MVP, pragmatic): allow `'self'` for scripts/styles/images/fonts + hashed assets. If using **Google Fonts** and/or **Bootstrap CDN**, include their hosts explicitly.
    - Phase 2: remove `unsafe-inline` by switching to nonces/hashes; pin exact domains in allow-list.
  - **Auth cookies:** `Secure`, `HttpOnly`, `SameSite=Lax` (or `Strict` if UX allows)

---

## Caching & Performance

- **Hashed assets (JS/CSS/images):** `Cache-Control: public, max-age=31536000, immutable`
- **HTML pages:** `no-cache` (or short), so new/edited posts appear immediately
- **Compression:** gzip (Brotli later if desired)
- **ETag/Last-Modified:** for conditional requests on static

---

## WebSockets Readiness

- **NPM:** WebSocket toggle **ON** for the apex proxy; consider longer timeouts for streaming
- **App:** `/ws` supports topics; echo test for smoke checks
- **Islands:** optional WS use for live preview, chat, notifications
- **Scale later:** add Redis/pub-sub or sticky sessions if running multiple replicas

---

## Content & SEO Essentials

- **Canonical URLs**, **OpenGraph/Twitter** meta, unique `<title>` + `<meta description>`
- **Article structured data** (BlogPosting schema) — add post-MVP or now if easy
- **Robots.txt** (allow public, disallow admin)
- **RSS (`/feed.xml`)** in MVP; **sitemap** shortly after MVP
- **Slug strategy:** lowercase, hyphenated, stable; redirect if changed

---

## MVP Scope (must-have)

- Public pages: `/`, `/posts`, `/posts/{slug}` (SEO-complete)
- Admin pages: `/admin`, `/admin/posts`, `/admin/posts/new`, `/admin/posts/{id}/edit`
- WYSIWYG editor island with image upload
- Auth: login + session (basic); server-side CSRF if needed for forms
- APIs: posts CRUD, media, auth, health, config
- WebSockets: echo endpoint + admin preview topic
- RSS feed
- Baseline CSP + headers
- NPM config validated (TLS, proxy, WS)

---

## Milestones & Acceptance Criteria (no code, all verifiable)

_(Milestones 1–8 remain the same as before; unchanged for brevity.)_

---

## NPM Configuration (edge, separate container)

- **Proxy Host:** apex domain → `http://<app-service>:<port>`
- **SSL:** Let’s Encrypt enabled; **Force SSL** redirect
- **WebSockets:** ON
- **HSTS:** ON when ready to commit to HTTPS sitewide
- **Optional:** custom security headers, increased timeouts/body size if needed

---

## CSP Allow-List (starter)

- Always: `'self'` for script/style/img/font/connect
- If using **Google Fonts**:
  - `fonts.googleapis.com` (style), `fonts.gstatic.com` (font)
- If using **Bootstrap** via CDN:
  - `cdn.jsdelivr.net` **or** `cdnjs.cloudflare.com` (pick one to minimize scope)
- WebSockets:
  - `connect-src` includes `wss://yourdomain.com`
- Tighten over time; remove unused hosts; add nonces/hashes to drop `unsafe-inline`

---

## Operational Runbook (smoke tests)

1. **HTML:** `GET /` (200) → view source shows post titles inline
2. **API:** `GET /api/health` → shows build version
3. **Assets:** `GET /static/assets/app.[hash].js` → `Cache-Control: immutable`
4. **Routing:** direct-load `/posts/{slug}` (no client router needed)
5. **WS:** connect to `wss://yourdomain.com/ws` and echo a message
6. **Admin:** open `/admin/posts/new` → editor island visible; save draft → preview updates
7. **RSS:** `GET /feed.xml` → includes the latest post

---

## Notes on Design Libraries

- **Bootstrap:** quickest way to a clean UI (forms/tables) with minimal custom CSS; include in CSP if you use a CDN.
- **Tailwind:** great control and theming; adds a build step for CSS utilities—consider after MVP.
- **Fonts:** default system fonts are fine to start; add **Google Fonts** later if you want brand polish (update CSP accordingly).

---

## Parking Lot (post-MVP)

- **Sitemap** & **Article structured data**
- Image optimization pipeline (thumbs, WebP/AVIF)
- Search with typo-tolerance (server-rendered page + filter island)
- Role-based admin (authors, editors)
- CDN fronting (optional) for assets
- Blue/green deploys (if you want instant cutovers later)

---

### How to Use This Document

- Treat it as your **source of truth** for intent and boundaries.
- You can hand this to any collaborator (or future you) to **start building immediately** without re-explaining past decisions.
- When you change a decision (e.g., adopt Tailwind, add sitemap), annotate this doc in `docs/` and bump the version in `/api/health`.
