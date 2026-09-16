# Radial — Research Intelligence Workspace
## Project Documentation (as of current build)

A modern React dashboard that gives researchers a single pane of glass over their **research portfolio** — tracking trends, patents, funding opportunities, citations, collaborations, and overall **innovation health**.

---

## 1. Project Objectives & Innovation Intelligence Workflows

### Objectives

- Provide a unified workspace where researchers can monitor their research portfolio, citation momentum, patent pipeline, and funding fit.
- Deliver actionable **innovation intelligence**: quantified innovation score, opportunity matching, trend detection, and exportable reports.
- Support secure sign-in (Google OAuth + local credentials) with a clear path toward role-based access.
- Ship a polished, responsive UI where every visible element is functional.
- Be deployable to production hosting (Vercel) with server-side secret handling.

### Core workflows

1. **Authenticate & enter workspace** — Google OAuth (PKCE) or email + name; demo mode when no credentials are configured.
2. **Portfolio overview** — home hero + quick stats; dashboard with portfolio health ring, research momentum bars, activity log, opportunity pipeline, trend radar, and patent pipeline.
3. **Funding intelligence** — grants ranked by semantic fit; save opportunities to portfolio.
4. **Patent intelligence** — track filings, statuses, jurisdictions; search and filter.
5. **Publication intelligence** — citation/h-index stats, searchable record, DOI deep links.
6. **Innovation scoring** — overall score ring, metric breakdown vs. targets, comparative benchmarks, suggested improvements.
7. **Reporting** — downloadable reports and generated innovation briefs.
8. **Collaboration network** — ranked partner suggestions by topic overlap.
9. **Lab resource management** — availability status and booking requests.
10. **Alerts** — patent/grant/citation/system notifications with read-state management.
11. **Settings & data management** — profile, notification preferences, data sources, account links, data export.

---

## 2. System Architecture & Database Schema

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Browser (React 18 SPA)                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐   │
│  │ AppShell      │  │  Pages       │  │  lib/            │   │
│  │ sidebar/topbar│  │  (routes/)   │  │  auth-context,   │   │
│  │ sign-in       │  │  file-based  │  │  oauth, data     │   │
│  └──────────────┘  └──────────────┘  └──────────────────┘   │
└─────────────────────────────────────────────────────────────┘
            │  /api/oauth/exchange/* (dev: Vite proxy)
┌──────────────────────────▼──────────────────────────────────┐
│  Exchange Server (Express, server/index.mjs)                │
│  · POST /api/oauth/exchange/google                          │
│  · GET  /health                                             │
│  · Holds GOOGLE_CLIENT_SECRET (never shipped to browser)    │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTPS
        ┌──────────────────▼──────────────────┐
        │  Google OAuth 2.0 Token + ID token  │
        └─────────────────────────────────────┘
```

**Production (Vercel):** the frontend is built to `dist/`; `vercel.json` rewrites `/api/*` to the serverless function at `api/index.mjs` (the same Express app) and all other routes to `index.html` for SPA routing.

### Data models (current — `src/lib/data.ts`)

| Model | Key fields |
| --- | --- |
| `Trend` | title, growth, citations, description, tags |
| `ActivityItem` | type, message, time |
| `Patent` | id, number, title, status (`granted`/`examination`), filingDate, inventors[], jurisdictions[] |
| `Funding` | id, title, funder, amount, deadline, fit (0–100), badges[] |
| `Publication` | id, title, authors[], venue, year, citations, doi |
| `ScoreMetric` | label, value, target, hint |
| `Report` | id, title, type (PDF/DOCX), date, size, snippet |
| `Collaborator` | id, name, institution, topics[], score |
| `Resource` | id, name, type, status (`available`/`in-use`/`maintenance`), location |
| `AlertItem` | id, type, message, time, read |
| `AuthUser` | sub, name, email, picture, provider (`google`/`demo`/`email`) |
| `UserProfile` (profile) | name, title, affiliation, bio, interests[], metrics[], recentActivity[], affiliations[] |

### Persistence (current)

- **Session**: `localStorage` (`radial.auth.user`) for the signed-in user; `sessionStorage` for the PKCE verifier/state during OAuth.
- **Domain data**: static mock datasets in `src/lib/data.ts` (no backend DB yet). Bookmarks, alert read-state, and lab booking state are client-side UI state.

### Proposed production database schema (PostgreSQL, future)

```sql
-- Users & roles
CREATE TABLE users (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  provider      TEXT NOT NULL,              -- 'google' | 'email'
  sub           TEXT UNIQUE,                -- external subject id
  email         TEXT UNIQUE NOT NULL,
  name          TEXT NOT NULL,
  picture       TEXT,
  role          TEXT NOT NULL DEFAULT 'researcher', -- researcher | principal_investigator | admin
  created_at    TIMESTAMPTZ DEFAULT now()
);

-- Researcher profile
CREATE TABLE profiles (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id       UUID UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  affiliation   TEXT,
  title         TEXT,
  bio           TEXT,
  interests     TEXT[],
  timezone      TEXT DEFAULT 'UTC'
);

-- Domain tables
CREATE TABLE publications (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id       UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  doi           TEXT,
  title         TEXT NOT NULL,
  venue         TEXT,
  year          INT,
  authors       TEXT[],
  citations     INT DEFAULT 0
);

CREATE TABLE patents (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id       UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  number        TEXT NOT NULL,
  title         TEXT NOT NULL,
  status        TEXT NOT NULL,              -- 'granted' | 'examination'
  filing_date   DATE,
  inventors     TEXT[],
  jurisdictions TEXT[]
);

CREATE TABLE funding_opportunities (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id       UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  title         TEXT NOT NULL,
  funder        TEXT,
  amount        TEXT,
  deadline      DATE,
  fit           INT,
  saved         BOOLEAN DEFAULT false
);

CREATE TABLE notifications (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id       UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  type          TEXT NOT NULL,              -- 'patent' | 'grant' | 'citation' | 'system' | 'collab'
  message       TEXT NOT NULL,
  read          BOOLEAN DEFAULT false,
  created_at    TIMESTAMPTZ DEFAULT now()
);
```

---

## 3. UI Wireframes & Workflow Planning

### Application shell

```
┌────────────┬──────────────────────────────────────────────┐
│  Sidebar   │  Top bar (hamburger · page title · alerts ·  │
│  (drawer on│           user menu)                         │
│  mobile)   ├──────────────────────────────────────────────┤
│  Logo      │                                              │
│  Nav       │                    Page content              │
│  (collapse)│                                              │
│            │                                              │
└────────────┴──────────────────────────────────────────────┘
```

### Page inventory

| Route | Purpose | Key components |
| --- | --- | --- |
| `/` | Home | Hero (welcome banner), quick stats, new trends, recent activity |
| `/dashboard` | Overview | ScoreRing, ProgressBars, activity log, opportunity pipeline, trend radar, patent pipeline |
| `/patents` | Patent portfolio | Search + status filter, patent cards |
| `/funding` | Grant recommendations | Fit-badged cards, save-to-portfolio toggle |
| `/publications` | Publication record | Stats, live search, DOI links |
| `/innovation-score` | Scoring | ScoreRing, metric breakdown, benchmarks, improvements |
| `/reports` | Reporting | Report cards (real downloads), export center |
| `/collaborations` | Partner network | Partner cards, recommendation engine note |
| `/lab-resources` | Equipment | Availability cards, booking requests |
| `/alerts` | Notifications | Unread/read lists, mark-as-read |
| `/settings` | Configuration | Profile, notifications, data sources, accounts, export |
| `/profile` | Researcher profile | Identity card, metrics, affiliations, activity |
| `/auth/callback` | OAuth return | Spinner while exchanging code |

### Design system

- **Dark slate shell** (`#0F172A → #1E293B` page gradient) with white rounded-2xl cards.
- **Gradients**: primary blue→cyan (`#2563EB → #06B6D4`), secondary purple (`#7C3AED → #A855F7`), accent teal (`#14B8A6 → #2DD4BF`), hero (`#0F172A → #2563EB → #06B6D4`).
- **Type**: Fraunces (serif headings) + Public Sans (body); **icons**: Lucide; **toasts**: Sonner.
- **Feedback**: hover lift on cards, brightness/glow on buttons, disabled states, focus rings on inputs.

---

## 4. Frontend & Backend Environment Setup

### Frontend

- **Stack**: React 18 + TypeScript + Vite 5.
- **Routing**: TanStack Router (file-based — each file in `src/routes/` is a page; `routeTree.gen.ts` is auto-generated).
- **Styling**: Tailwind CSS 3 with custom design tokens in `tailwind.config.js` (gradient utilities, card/glow shadows) and CSS variables in `src/index.css`.
- **Dev server**: Vite on `http://localhost:5173`, proxies `/api` → `http://localhost:3001`.

### Backend

- **Stack**: Express (`server/index.mjs`), CORS, Node built-in `fetch`.
- **Routes**: `GET /health`, `POST /api/oauth/exchange/google`.
- **Secrets**: loaded from `.env` via `--env-file-if-exists` (never in the browser).
- **Production**: same app is exported as the Vercel serverless function `api/index.mjs` (listens only when run directly).

### Environment variables (`.env`, gitignored; template in `.env.example`)

| Variable | Where | Purpose |
| --- | --- | --- |
| `VITE_GOOGLE_CLIENT_ID` | browser | Google OAuth client ID |
| `VITE_OAUTH_EXCHANGE_URL` | browser | Exchange endpoint (defaults to `/api/oauth/exchange`) |
| `GOOGLE_CLIENT_ID` | server | Server-side client ID |
| `GOOGLE_CLIENT_SECRET` | server | **Secret** — required for token exchange |
| `PORT` | server | Exchange port (default 3001) |

### Commands

| Command | Description |
| --- | --- |
| `npm install` | Install dependencies |
| `npm run dev:full` | Run exchange server + Vite together |
| `npm run dev` | Vite only |
| `npm run server` | Express exchange server only |
| `npm run build` | Production build to `dist/` |
| `npm run preview` | Preview production build |
| `npx tsc --noEmit` | Type check |

---

## 5. Authentication & Role-Based Access System

### Implemented (current)

1. **Google OAuth 2.0 (Authorization Code + PKCE)**
   - `src/lib/oauth.ts` builds the authorize URL with `code_challenge` (S256), stores `code_verifier`/`state` in `sessionStorage`, redirects to Google.
   - Google redirects to `/auth/callback?code=&state=` (`src/routes/auth.callback.tsx`).
   - The client POSTs the code to the exchange server, which swaps it for tokens using `GOOGLE_CLIENT_SECRET` and returns the profile (sub, name, email, picture).
   - Requires the redirect URI `http://localhost:5173/auth/callback` (or production URL) to be registered in Google Cloud Console.

2. **Credential sign-in (email + name)**
   - `signInWithCredentials(email, name)` in `src/lib/auth-context.tsx` validates and creates a local session.

3. **Demo mode**
   - Active when no OAuth client ID is configured; uses a demo profile so the UI is always explorable.

4. **Session persistence**
   - `AuthUser` stored in `localStorage`; sign-out clears it and returns home.

### Role-based access control (design, not yet implemented)

| Role | Access |
| --- | --- |
| `researcher` | Own portfolio, publications, patents, funding, alerts |
| `principal_investigator` | `researcher` + team/collaboration management, report export |
| `admin` | All above + user administration, data-source management, settings |

Implementation plan:
- Add `role` to the `users` table and return it from the exchange/profile endpoint.
- Guard routes with a `requireRole('principal_investigator')` check in `__root.tsx` or per-route `beforeLoad`.
- Gate UI actions (e.g., export, admin settings) by role.

---

## 6. Research Profile Management Workflows

1. **Identity** — name, title, affiliation, bio, research interests, verified-researcher badge, avatar (Google picture or initials).
2. **Metrics** — publications, citations, h-index, patents, grants won.
3. **Affiliations** — institutional memberships (University of Geneva, ETH Zurich, NIS Singapore).
4. **Activity** — recent actions (patents filed, grants awarded, publications).
5. **Settings** (`/settings`)
   - Profile: display name, institutional email, primary affiliation, time zone (validated save).
   - Notifications: toggle per category (deadlines, patents, citations, reports).
   - Data sources: connected (ORCID, Scopus, USPTO/EPO) vs. not connected (Dimensions).
   - Connected accounts (Google Scholar, X, LinkedIn).
   - Data export: downloads the workspace data as JSON.
6. **Persistence** — session user drives name/email; profile enrichment is currently mock data, ready to be sourced from the `profiles` table.

---

## 7. Publication & Patent Datasets Integration

### Publications

- **Stats**: total citations, h-index, publication count, recent citations.
- **Search**: live client-side filter by title, venue, or author.
- **List**: title, authors, venue, year, citation count, and a working **DOI** deep link (`https://doi.org/<doi>`).
- **Source data**: `publications` + `pubStats` in `src/lib/data.ts`.

### Patents

- **Portfolio**: number, title, status badge (Granted / Under Examination), filing date, inventors, jurisdictions.
- **Search & filter**: live filter by title/number/inventor and by status.
- **Source data**: `patents` in `src/lib/data.ts`.

### Integration roadmap (future)

1. Replace mock arrays with API-backed data via ORCID Public API (publications), Scopus/OpenAlex (citations), and USPTO/EPO (patents).
2. Add ingestion jobs that refresh datasets and generate `notifications` (e.g., citation milestones, patent status changes).
3. Persist bookmarks, read-state, and bookings in the `funding_opportunities` / `notifications` / resource tables.
4. Expose the exchange server's data endpoints behind the same `/api` proxy.

---

## Appendix — Repository Layout (`radial/`)

```
radial/
├── api/index.mjs            # Vercel serverless function (Express app)
├── server/index.mjs         # OAuth exchange server (local dev)
├── src/
│   ├── components/          # app-sidebar, top-bar, sign-in, ui primitives
│   ├── lib/                 # auth-context, oauth, oauth-config, data, utils
│   ├── routes/              # one file per page + __root.tsx + auth.callback.tsx
│   ├── index.css            # design tokens / gradients
│   ├── main.tsx             # app entry
│   └── routeTree.gen.ts     # auto-generated route manifest
├── vercel.json              # rewrites: /api → function, SPA fallback
├── .env.example             # env template (never commit .env)
├── tailwind.config.js       # gradient/shadows design tokens
└── package.json
```
