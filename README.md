# Issa Abdulsalam Opeyemi -- Portfolio

Personal portfolio site for **Issa Abdulsalam Opeyemi**, backend developer
(Django, Django REST Framework, SQL), mobile developer (Flutter), currently
picking up **Go** for concurrency. Built with plain Django templates -- no
frontend framework, no build step.

Live pages:

- `/` -- landing page: about, education, skills
- `/projects/` -- full reviews of every project (stack, links, status)
- `/cv/` -- view CV inline, or download it
- `/sitemap.xml`, `/robots.txt`, `/llms.txt` -- SEO / GEO endpoints

## Project structure

```
P_FOLIO/              Django project config (settings, root urls)
portfolio/             The one app that owns every visible page
  data.py               Static project list (no DB -- edit this file to
                         add/change a project)
  views.py              Landing, projects, CV view/download, robots/llms
  templates/portfolio/  Page templates (each extends base_template.html)
  static/portfolio/
    css/critical.css     (moved into templates/base/, see below)
    css/styles.css       Full stylesheet, loaded via preload+swap
    js/main.js           Mobile nav toggle only
    images/               <- put profile.jpg / favicon.png here
    files/                 <- put your CV PDF here
utility/                Site-wide config (name, links, SEO defaults) +
                        the context processor that injects it as {{ site }}
                        into every template
templates/
  base/base_template.html  The single base template every page extends
                            (also holds the overridable SEO/OG meta blocks)
  base/critical.css        Above-the-fold CSS, inlined into <head>
  seo/robots.txt, llms.txt  Plain-text SEO/GEO endpoints
```

## Local setup

1. Create and activate a virtual environment:
   ```
   python -m venv venv
   venv\Scripts\activate        (Windows)
   ```
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Run the dev server:
   ```
   python manage.py runserver
   ```
4. Visit `http://127.0.0.1:8000/`

Personal portfolio -- all rights reserved by Issa Abdulsalam Opeyemi.
