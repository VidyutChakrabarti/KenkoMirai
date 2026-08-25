<div align="center">

# KenkoMirai Web

### Same-origin scenario controls and dependency-light visualization

<p>
  <a href="../README.md"><img alt="Project overview" src="https://img.shields.io/badge/BACK-PROJECT_OVERVIEW-B8E7D1?style=for-the-badge&labelColor=101815&color=365D4D"></a>
  <a href="../docs/setup.md"><img alt="Setup guide" src="https://img.shields.io/badge/OPEN-SETUP_GUIDE-B8E7D1?style=for-the-badge&labelColor=101815&color=477A65"></a>
  <a href="../docs/gallery.md"><img alt="Project gallery" src="https://img.shields.io/badge/VIEW-PROJECT_GALLERY-B8E7D1?style=for-the-badge&labelColor=101815&color=365D4D"></a>
</p>

</div>

---

The canonical frontend is a Next.js application with overview, scenario-lab, and operations pages. Browser API requests use `/api/backend/*`; the server-side gateway forwards them to `KENKOMIRAI_API_URL/api/v1/*`. The gateway timeout is configured with `KENKOMIRAI_GATEWAY_TIMEOUT_MS` and distinguishes upstream failure (`502`) from timeout (`504`).

No map tiles, marker assets, random browser data, Axios client, Leaflet runtime, or Chart.js lifecycle is required. Agent positions and a rolling 1,000-sample per-hour SEIRD trajectory render as accessible SVG; the API retains the configured full session history. The scenario ID is retained in session storage and restored with the bounded history endpoint after a page refresh.

## Commands

Run these from the repository root so the committed workspace lockfile is used:

```bash
npm ci
npm run dev
npm run lint
npm run build
```

Set `KENKOMIRAI_API_URL` in the Next.js server environment. Do not expose private backend hostnames through `NEXT_PUBLIC_*` variables.

## Routes

| Route | Purpose |
|---|---|
| `/` | Product overview and model scope |
| `/simulation` | Create and advance an interactive scenario |
| `/dashboard` | API readiness and session capacity |
| `/api/backend/[...path]` | Restricted GET/POST/DELETE API gateway |

See [the setup guide](../docs/setup.md) for container and Kubernetes operation.
