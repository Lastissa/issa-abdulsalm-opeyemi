# Portfolio

A simple portfolio site to showcase work and updates. 

| Route | Purpose |
| --- | --- |
| `/` | Home |
| `/projects` | Projects |
| `/feed` | Updates |
| `/cv` | CV |
| `/login` | Sign in |
| `/custom-admin` | Owner area |

Django templates, one stylesheet, a small JavaScript file, and locally vendored HTMX and Alpine. No build step.

## Features

- Clean, mobile-friendly design
- Projects and updates sections
- CV view and download
- Owner area for managing content
- Light and dark theme toggle
- Splash screen on first load

## Setup

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
```

Run migrations and create an account:

```bash
python manage.py migrate
python manage.py createsuperuser
```

To add missing default content:

```bash
python manage.py seed_content
```

Start the development server:

```bash
python manage.py runserver
```

Upload a CV and publish a post from `/custom-admin` after signing in at
`/login`.

## Editing site content

- `/admin/portfolio/` contains the editable content models. Most models have
  inline or list-editable fields so routine updates do not require code changes.
- `Site settings` is a singleton row: identity, SEO copy, hero copy, contact
  copy, CV display name, toast position, and default theme.
- `Page content` holds the eyebrow, heading, intro, and metadata for the
  projects, feed, CV, and login pages.
- `Projects` include the case-study fields and an inline stack editor.
- CV files are managed at `/custom-admin/cv/`; old versions remain available
  until deleted, and exactly one version can be active.

The public site is cached as a single payload for ten minutes. Saving or
deleting any content model invalidates that cache automatically.

## Database

- `DEBUG=True` uses SQLite
- `DEBUG=False` uses PostgreSQL. Set `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `DB_SSLMODE` in `.env`. If any are missing, the app will fail to start.

## Storage

- `DEBUG=True` uses local files
- `DEBUG=False` uses S3. Set `AWS_ENDPOINT_URL_S3`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION`, `S3_BUCKET` in `.env`. CVs are streamed through the app.

## Environment

| Variable | Default | Notes |
| --- | --- | --- |
| `DEBUG` | `False` | Use `True` locally; `False` on HTTPS production |
| `DB_NAME` | empty | Required when `DEBUG=False` |
| `DB_USER` | empty | Required when `DEBUG=False` |
| `DB_PASSWORD` | empty | Required when `DEBUG=False` |
| `DB_HOST` | empty | Required when `DEBUG=False` |
| `DB_PORT` | `5432` | PostgreSQL port |
| `DB_SSLMODE` | `require` | PostgreSQL SSL mode |
| `DB_CONN_MAX_AGE` | `60` | Persistent DB connection lifetime in seconds |
| `AWS_ENDPOINT_URL_S3` | empty | Required when `DEBUG=False` |
| `AWS_ACCESS_KEY_ID` | empty | Required when `DEBUG=False` |
| `AWS_SECRET_ACCESS_KEY` | empty | Required when `DEBUG=False` |
| `AWS_REGION` | empty | Required when `DEBUG=False` |
| `S3_BUCKET` | empty | Required when `DEBUG=False` |
| `ALLOWED_HOST` | localhost, 127.0.0.1, and ngrok host | Comma-separated |
| `FULL_DOMAIN` | `http://localhost:8000` | Used in canonical/OG/sitemap/RSS |
| `CSRF_TRUSTED_ORIGINS` | empty | Comma-separated, needed behind a proxy |
| `SY_SECRET` | empty | Required by the flush endpoint |

Generate a token:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## Analytics

Every public GET request increments cache counters keyed by path and day. The
middleware skips staff users, bots, static/media files, HTMX fragments, and
private routes.

Flush the cache every five minutes with either:

```bash
python manage.py flush_analytics
```

or the HTTP endpoint:

```bash
curl -fsS -X POST \
  -H "Authorization: Bearer $SY_SECRET" \
  https://your-domain.com/custom-admin/api/analytics/flush/
```

Example cron entry:

```cron
*/5 * * * * curl -fsS -X POST -H "Authorization: Bearer $SY_SECRET" https://your-domain.com/custom-admin/api/analytics/flush/ >/dev/null 2>&1
```

The endpoint returns JSON with a consistent `status` and `detail`, plus the
flush result:

```json
{
  "status": "ok",
  "detail": "Flushed 42 views.",
  "result": {
    "ok": true,
    "days": 1,
    "page_rows": 3,
    "visitor_rows": 4,
    "views": 42
  },
  "ok": true
}
```

A cache lock prevents two flushes from running at the same time. If the token is
not configured, the endpoint returns `503` and does nothing. Visitor records
store only a salted hash, never a raw IP address. The dashboard can search,
export CSV, and delete records.

## JSON and HTMX conventions

- JSON endpoints return at least `{ "status": "ok|error", "detail": "..." }`.
  Login/logout may also include `redirect`; the analytics flush includes
  `result` and `ok`.
- HTMX mutation endpoints return an HTML fragment, or an empty `200` with
  `HX-Trigger`/`HX-Redirect` headers. Delete endpoints deliberately use `200`
  with an empty body so `hx-swap="delete"` removes the row.
- Toasts are triggered by Django messages on page load or by the `toast` key in
  an `HX-Trigger` response. The position is controlled by
  `SiteSettings.toast_position`.
- The login form posts JSON with `X-Requested-With: XMLHttpRequest`, disables and
  blurs its submit button while the request is in flight, and keeps the button
  locked while the browser follows a successful redirect.

## Static files

```bash
python manage.py collectstatic --noinput
```

WhiteNoise serves static files. HTMX and Alpine are vendored locally. CVs are served through Django views.

## Project layout

```
P_FOLIO/           settings, URLs
portfolio/         apps, views, models, templates, static
templates/         base and SEO templates
service_internal/  cache and context helpers
```

## Notes

- Set `FULL_DOMAIN` in production for correct links.
- Analytics flushes via `/flush-cache/` or `python manage.py flush_analytics`.
