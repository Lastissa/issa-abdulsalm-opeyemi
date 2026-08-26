# workflow.md

Every non-obvious decision made while building this project, and why.
Read this if you're wondering "why is it structured like this


## 1. Architecture

### Decision P1 -- Projects are static Python data, not a database model

I explicitly chose this (static file over DB-driven admin). Given
there's also no contact form and no other write path, this project
ends up with **zero custom models**. That's the right amount of
engineering for a personal portfolio with content that changes maybe
once a month: a Django `Project` model + admin + migrations would be
three extra moving parts (a DB table, an admin registration, a
migration file to keep in sync) for something a single Python list
already does. [portfolio/data.py`](portfolio/data.py)is fully documented inline.


### Decision P2 -- One Django app (`portfolio`)

Landing, projects, and CV all live in a single `portfolio` app. Three
pages sharing one context (site config) don't need app-level isolation. Splitting them
into `about`, `projects`, `cv` apps would mean three `apps.py`, three
`urls.py`, three entries in `INSTALLED_APPS` for zero practical
benefit at this size.

### Decision U1 -- A root-level `utility/` package (not a Django app) for shared config

A `UTILITY` folder [click here](utility/) at the project root
with a config file feeding a custom context processor. It's a plain
Python package, not a Django app , because it holds no models, no views, no
migrations -- just a config module and a context processor function.

### Decision T1 -- `templates/base/base_template.html` at the project root

It lives in a **project-level** `templates/` directory (added to
`TEMPLATES['DIRS']` in settings), not inside the `portfolio` app,
because it's shared infrastructure -- if a second app is ever added
(say, a blog), it should extend the same base template without
importing from the `portfolio` app. Page-specific templates
(`landing.html`, `projects.html`, `cv.html`) live in
`portfolio/templates/portfolio/` (Django's standard app-template
convention, found automatically via `APP_DIRS`) and each starts with
`{% extends "base/base_template.html" %}`.

`templates/seo/_meta.html` is a separate include, not directly added into
`base_template.html` directly, so the `<title>`/meta/OG block can be
swapped or extended independently of the rest of the `<head>` without
touching the base template.

### Decision F1 -- No contact form

This avoids needing a `Message` model,
a `ModelForm`, CSRF-aware POST handling, and either an email backend
or a spam-prone open endpoint, all for a feature that a `mailto:`
link and a GitHub/LinkedIn link do just as well for a portfolio site.
Social links render conditionally [(see `utility/config.py` ->
`SOCIAL_LINKS`)](utility/config.py/)
---

## 2. SEO and GEO

"GEO" means **Generative Engine Optimization** -- making the site
legible to AI answer engines.

### Decision S1 -- `django.contrib.sitemaps`, not a hand-rolled sitemap

Django ships a sitemap framework; `portfolio/sitemaps.py` defines a
tiny `StaticViewSitemap` listing the three real URLs with priorities.
Wired at `/sitemap.xml` in `P_FOLIO/urls.py`. Three lines of
configuration versus hand-writing and maintaining raw XML.

### Decision S2 -- `llms.txt`

An emerging (not yet universally standardized) convention where a
site exposes a plain-text, structured summary of itself at `/llms.txt`
specifically for AI crawlers to consume, separate from the
HTML-oriented `robots.txt`/sitemap. Implemented as a Django view
(`portfolio/views.py` -> `llms_txt`) rendering
`templates/seo/llms.txt`, reusing the same `site` config and
`PROJECTS` data as the rest of the site -- so it can never drift out
of sync with what's actually on the pages.

### Per-page structured data (JSON-LD)

- **Landing (`/`)**: `schema.org/Person` -- name, job title, skills
  (`knowsAbout`), GitHub (`sameAs`), university (`alumniOf`). This is
  the block that lets a search engine or AI assistant answer "who is
  Issa Abdulsalam Opeyemi" directly and correctly from the page.
- **Projects (`/projects/`)**: `schema.org/ItemList` of
  `SoftwareSourceCode` entries -- one per project, with repo URL and
  primary stack item. Lets each project be individually understood as
  a discrete work.

- **CV (`/cv/`)**: `schema.org/ProfilePage` wrapping the same `Person`
  identity, so the CV page is understood as *about* the same entity as
  the landing page.

---

## 3. Performance (the "TTL"/TTI concern)

### Decision C3 -- CSS split into critical + main stylesheet

`templates/base/critical.css` holds only
what's needed to correctly paint the header, nav, and hero on the
very first frame (CSS variables, body background/color, header/hero
layout and type) and is **inlined directly into `<head>`** via
`{% include %}` in `base_template.html` -- No round-trip for above-the-fold styling. `portfolio/static/portfolio/css/styles.css`
holds everything else (sections, cards, footer, responsive rules,
animation) and is loaded with a preload-then-swap pattern:

```html
<link rel="preload" href="...styles.css" as="style" onload="this.rel='stylesheet'">
<noscript><link rel="stylesheet" href="...styles.css"></noscript>
```

This tells the browser to fetch `styles.css` at high priority without
blocking rendering on it, then apply it once it arrives. The
`<noscript>` fallback covers the (rare) no-JS case so the site never
looks broken.

`critical.css` lives in `templates/base/` (a template, not a static
file) specifically so it can be inlined via `{% include %}` --
Django's template loader can't `{% include %}` a file from a static
directory, only from a template directory.

### Decision C2 -- WhiteNoise for static file serving

Added `whitenoise` (one dependency) with
`CompressedManifestStaticFilesStorage`. In production this serves
`collectstatic`'s output with hashed filenames (so browsers cache them
forever and safely bust the cache on redeploy) and gzip/br
compression, directly from Django

### Decision C4 -- Vanilla JS, no framework/bundler

`main.js` is ~15 lines doing exactly one thing (mobile nav toggle).
 the entire site is server-rendered.

### Fonts

Google Fonts, loaded via `<link>` with `display=swap` and
`rel="preconnect"` hints fired before the stylesheet link. `swap`
means text renders immediately in a fallback font and swaps to the
webfont when it arrives, instead of showing invisible text
(`font-display: block`, the browser default) while waiting.
