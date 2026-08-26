# workflow.md

Every non-obvious decision made while building this project, and why.
Read this if you're wondering "why is it structured like this" before
changing something.

---

## 0. What I did and didn't run

Per your instruction, I did not run `pip install`, `makemigrations`,
`migrate`, `runserver`, `collectstatic`, or any other terminal command
against this project. Every file was hand-written and reviewed. That
also means Django itself never actually executed this code before it
reached you -- follow the setup steps in `README.md` and if something
throws an error on first run, it's likely a small typo, not a design
flaw. Most likely spots: a missing static file (CV/images, expected --
see the READMEs in those folders) or a typo in a template tag.

There are no migration files in this repo because there are no custom
models -- projects are static Python data (decision P1), and there's
no contact form (decision F1), so the only tables Django needs are the
default `auth`/`admin`/`sessions` ones, which `migrate` creates from
Django's own built-in migrations. You still need to run `migrate`
once, locally, for the admin login and sessions to work.

---

## 1. Architecture

### Decision P1 -- Projects are static Python data, not a database model

You explicitly chose this (static file over DB-driven admin). Given
there's also no contact form and no other write path, this project
ends up with **zero custom models**. That's the right amount of
engineering for a personal portfolio with content that changes maybe
once a month: a Django `Project` model + admin + migrations would be
three extra moving parts (a DB table, an admin registration, a
migration file to keep in sync) for something a single Python list
already does. `portfolio/data.py` is fully documented inline -- adding
a project is "add a dict to a list."

If this ever needs to be editable by someone non-technical, or grows
past ~20 projects with filtering/search, that's the trigger to
revisit and move to a real model. Not before.

### Decision P2 -- One Django app (`portfolio`), not one-app-per-page

Landing, projects, and CV all live in a single `portfolio` app. Three
pages sharing one context (site config, no auth-gated content, no
distinct data models) don't need app-level isolation. Splitting them
into `about`, `projects`, `cv` apps would mean three `apps.py`, three
`urls.py`, three entries in `INSTALLED_APPS` for zero practical
benefit at this size.

### Decision U1 -- A root-level `utility/` package (not a Django app) for shared config

You asked for this explicitly: a `UTILITY` folder at the project root
with a config file feeding a custom context processor. It's a plain
Python package, not a Django app (no `apps.py`, not in
`INSTALLED_APPS`), because it holds no models, no views, no
migrations -- just a config module and a context processor function.
Making it a full Django app would be overhead for two files.

`utility/config.py` is the single source of truth for your name,
tagline, education, skills, SEO defaults, and social links.
`utility/context_processors.py` reads that config and injects it into
every template as `{{ site.* }}`, registered once in
`P_FOLIO/settings.py` -> `TEMPLATES` -> `context_processors`. Change a
link or your tagline in one file; it updates on every page
automatically -- this is the scalability lever you asked for.

### Decision T1 -- `templates/base/base_template.html` at the project root

You asked for a base template that every visible page extends. It
lives in a **project-level** `templates/` directory (added to
`TEMPLATES['DIRS']` in settings), not inside the `portfolio` app,
because it's shared infrastructure -- if a second app is ever added
(say, a blog), it should extend the same base template without
importing from the `portfolio` app. Page-specific templates
(`landing.html`, `projects.html`, `cv.html`) live in
`portfolio/templates/portfolio/` (Django's standard app-template
convention, found automatically via `APP_DIRS`) and each starts with
`{% extends "base/base_template.html" %}`.

`templates/seo/_meta.html` is a separate include, not baked into
`base_template.html` directly, so the `<title>`/meta/OG block can be
swapped or extended independently of the rest of the `<head>` without
touching the base template.

### Decision F1 -- No contact form

You chose links-only contact. This avoids needing a `Message` model,
a `ModelForm`, CSRF-aware POST handling, and either an email backend
or a spam-prone open endpoint -- all for a feature that a `mailto:`
link and a GitHub/LinkedIn link do just as well for a portfolio site.
Social links render conditionally (see `utility/config.py` ->
`SOCIAL_LINKS`) -- anything left as `""` just doesn't show up in the
footer, so you can fill them in gradually without breaking the layout.

---

## 2. SEO and GEO

"GEO" here means **Generative Engine Optimization** -- making the site
legible to AI answer engines (ChatGPT, Perplexity, Claude, etc.), not
geographic targeting (you didn't give a city, and the content isn't
location-dependent). If you actually meant geographic SEO, say so and
I'll add city/region structured data.

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
  a discrete work, not just prose in a card.
- **CV (`/cv/`)**: `schema.org/ProfilePage` wrapping the same `Person`
  identity, so the CV page is understood as *about* the same entity as
  the landing page, not a disconconnected document.

Every page also gets: a unique `<title>` (all built from
`{{ site.title }}` = "Issa Abdulsalam Opeyemi" so the exact name you
asked for is in every page's title and keywords), a real meta
description specific to that page's content, Open Graph + Twitter
card tags, and a canonical URL. These live directly in
`templates/base/base_template.html` as `{% block meta_title %}`,
`{% block meta_description %}`, etc. -- each page template overrides
only what's different (see `{% block meta_description %}` in each
page). Note: these blocks live in `base_template.html` itself rather
than a separate `{% include %}`'d partial, because Django's
`{% block %}` override mechanism only works through an
`{% extends %}` chain -- a block defined inside an included template
is invisible to child templates that extend the *including* template,
so it can't be overridden that way.

---

## 3. Performance (the "TTL"/TTI concern)

### Decision C3 -- CSS split into critical + main stylesheet

You asked for exactly this. `templates/base/critical.css` holds only
what's needed to correctly paint the header, nav, and hero on the
very first frame (CSS variables, body background/color, header/hero
layout and type) and is **inlined directly into `<head>`** via
`{% include %}` in `base_template.html` -- zero extra network
round-trip for above-the-fold styling. `portfolio/static/portfolio/css/styles.css`
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
compression, directly from Django -- no separate nginx or CDN
required to get solid cache headers on Render-style single-service
deploys, matching how your other projects are already hosted.

### Decision C4 -- Vanilla JS, no framework/bundler

`main.js` is ~15 lines doing exactly one thing (mobile nav toggle).
No React, no bundler, no build step -- the entire site is server-rendered
Django templates, so pulling in a JS framework for one interactive
element would add a build pipeline for negative benefit. Script tag
uses `defer` so it never blocks parsing.

### Fonts

Google Fonts, loaded via `<link>` with `display=swap` and
`rel="preconnect"` hints fired before the stylesheet link. `swap`
means text renders immediately in a fallback font and swaps to the
webfont when it arrives, instead of showing invisible text
(`font-display: block`, the browser default) while waiting.

---

## 4. Visual design decisions

Direction: a backend engineer who thinks in systems, not screens --
avoided the current default AI-portfolio looks (cream + terracotta;
near-black + neon; broadsheet/newspaper). Landed on a dark
ink/paper palette with a single amber "signal" accent, evoking log
output / status lights rather than a generic dark-mode theme.

- **Palette**: `--ink #0B0F14` (background), `--panel #121821` (cards),
  `--line #232B36` (hairline borders), `--paper #E8EDF2` (text),
  `--muted #8592A1` (secondary text), `--signal #F5A623` (the one
  accent colour -- links, active states, the primary button), `--ok
  #3ECF8E` (status pills only).
- **Type**: Space Grotesk for headings (technical, geometric
  character, used with restraint at weight 500 only), Inter for body
  copy (neutral, highly legible), JetBrains Mono for labels, tags,
  nav, and stack badges -- a deliberate nod to the terminal/code
  environment a backend developer actually works in, and it's what
  ties the whole UI together as "belongs to a developer" rather than
  "generic dark portfolio."
- **Signature element**: the animated request-flow diagram in the
  hero (`Client -> Django -> DRF API -> SQL DB`, with a dashed line
  and a moving pulse dot) is the one deliberate visual risk. It's not
  decoration -- it's literally the shape of the work described in the
  text next to it, and it echoes the "moving, not static" idea you
  described (currently exploring Go for concurrency) without needing
  a paragraph to explain it. `prefers-reduced-motion` disables the
  animation for anyone who's set that OS-level preference.
- **Everything else is quiet on purpose**: hairline borders, no
  shadows, no gradients, generous whitespace -- so the one signature
  element and the one accent colour actually stand out instead of
  competing with decoration.
- **Status pills** on the projects page ("Live", "In progress", "For
  sale", etc.) are literal and honest per your project descriptions
  -- including that the Lecture Tracker's reminder feature is
  currently broken. Never oversell an in-progress project as
  finished.

---

## 5. Accessibility (part of "best UI", not a separate checklist)

- Skip-to-content link, visible on keyboard focus.
- Visible focus rings (`:focus-visible`) on all interactive elements,
  using the signal colour so they're unmissable.
- All decorative SVG/icons are `aria-hidden`; the hero diagram has a
  proper `role="img"` + accessible label describing what it shows in
  words, for screen readers.
- Mobile nav toggle updates `aria-expanded`.
- Current nav item marked with `aria-current="page"`.
- Reduced motion respected (see above).
- Colour contrast: paper-on-ink and signal-on-ink both meet WCAG AA
  for body text at the sizes used.

---

## 6. Things deliberately left out (not over-engineering)

- No REST API for this site (you have DRF experience -- it's showcased
  *through the projects*, not needed to serve a personal site's own
  pages).
- No user accounts/auth beyond Django's default admin.
- No CMS, no rich-text editor, no database-backed content.
- No JS framework, no bundler, no `node_modules`.
- No per-project detail sub-pages -- all project reviews live on one
  page with in-page anchors (`/projects/#slug`), matching what you
  asked for ("this page once entered shows each project"), and
  keeping navigation to three real pages total, all of which rank
  well because there's no thin/duplicate content splitting authority
  across ten near-empty pages.
