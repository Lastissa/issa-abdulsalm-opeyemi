# Issa Abdulsalam Opeyemi - Portfolio, Feed, and Owner Dashboard

A Django portfolio rebuilt around four public routes and a private owner area:

| Route | Purpose |
| --- | --- |
| `/` | Home, profile, selected projects, skills, education |
| `/projects` | Project index with case-study links and live previews |
| `/feed` | Public, Facebook-style build feed (owner publishes) |
| `/cv` | Current CV, embedded and downloadable |
| `/login` | Owner sign-in (staff accounts only) |
| `/custom-admin` | Analytics dashboard, visitor records, posts, CV versions |

No frontend framework and no build step. Templates, one CSS file, and one small
JavaScript file.

## What changed

- **Owner area**: staff login, CV version history (activate/delete), feed
  composer, post editing/deletion, analytics dashboard.
- **Feed**: public posts with an optional external image URL. No image uploads.
- **Projects**: the index is now a clean card grid. Each project has its own
  case-study page with a browser-style iframe preview and fullscreen control.
- **Theme**: near-white light mode (`#ffffff`) and deep dark mode (`#070b10`),
  with a persistent toggle that respects the system preference on first visit.
- **Mobile-first CSS**: 44px+ tap targets, no horizontal scroll, responsive
  tables that become cards on small screens.
- **Modern SEO**: canonical URLs, Open Graph/Twitter cards, JSON-LD, RSS,
  `llms.txt`, and a sitemap that uses `lastmod` without the ignored
  `changefreq`/`priority` fields.
- **Cached analytics**: page views are counted in a file-based cache. A
  protected endpoint (or management command) flushes them to SQLite every five
  minutes. No database write on page load.

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

The project intentionally does not run migrations automatically. Run them once:

```bash
python manage.py makemigrations portfolio
python manage.py migrate
python manage.py createsuperuser
```

Then start the development server:

```bash
python manage.py runserver
```

Upload a CV and publish a post from `/custom-admin` after signing in at
`/login`.

## Environment

| Variable | Default | Notes |
| --- | --- | --- |
| `PRODUCTION` | `False` | Set to `True` on HTTPS production |
| `ALLOWED_HOST` | localhost + ngrok host | Comma-separated |
| `FULL_DOMAIN` | `http://localhost:8000` | Used in canonical/OG/sitemap/RSS |
| `CSRF_TRUSTED_ORIGINS` | empty | Comma-separated, needed behind a proxy |
| `ANALYTICS_FLUSH_TOKEN` | empty | Required by the flush endpoint |

Generate a token:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## Analytics

Every public GET request increments cache counters keyed by path and day. The
middleware skips staff users, bots, static/media files, and private routes.

Flush the cache every five minutes with either:

```bash
python manage.py flush_analytics
```

or the HTTP endpoint:

```bash
curl -fsS -X POST \
  -H "Authorization: Bearer $ANALYTICS_FLUSH_TOKEN" \
  https://your-domain.com/custom-admin/api/analytics/flush/
```

Example cron entry:

```cron
*/5 * * * * curl -fsS -X POST -H "Authorization: Bearer $ANALYTICS_FLUSH_TOKEN" https://your-domain.com/custom-admin/api/analytics/flush/ >/dev/null 2>&1
```

The endpoint returns JSON:

```json
{"ok": true, "days": 1, "page_rows": 3, "visitor_rows": 4, "views": 42}
```

A cache lock prevents two flushes from running at the same time. If the token is
not configured, the endpoint returns `503` and does nothing.

Visitor records store only a salted hash, never a raw IP address. The dashboard
can search, export CSV, and delete records.

## Static files

For production:

```bash
python manage.py collectstatic --noinput
```

WhiteNoise serves the collected files. Uploaded CVs live in `media/` and are
served through Django views (`/cv/file/` and `/cv/download/`), so access and
headers stay under application control.

## Project layout

```
P_FOLIO/                 settings, root URLs
portfolio/
  analytics.py           cache counters + flush logic
  data.py                static project content
  forms.py               login, feed, CV forms
  middleware.py          page-view middleware
  models.py              FeedPost, CVVersion, PageView, Visitor
  views.py               public pages + owner dashboard
  sitemaps.py            modern sitemap
  templates/portfolio/   public + dashboard templates
  static/portfolio/      CSS, JS, images, manifest, fallback CV
templates/base/          base layout + critical CSS
templates/seo/           robots.txt + llms.txt
utility/                 site identity/config
```

## Notes

- The bundled fallback CV at
  `portfolio/static/portfolio/files/issa-abdulsalam-opeyemi-cv.pdf` is used until
  the first upload. Uploading through `/custom-admin/cv/` takes over
  automatically.
- Feed images are external URLs only. Broken images are removed by the
  front-end instead of leaving an empty panel.
- The public feed is readable by anyone. Publishing and editing require a staff
  account.
