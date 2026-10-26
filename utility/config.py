from django.conf import settings


# --- Identity -----------------------------------------------------------
FULL_NAME = "Issa Abdulsalam Opeyemi"
SHORT_NAME = "Issa Abdulsalam"
SITE_TITLE = "Issa Abdulsalam Opeyemi"
ROLE_TITLE = "Backend Developer"
LOCATION = "Ilorin, Nigeria"

TAGLINE = "I build maintainable systems and the interfaces that make them usable."

# --- Canonical domain -----------------------------------------------------
# Every canonical/OG/sitemap URL in this project is derived from this value.
SITE_DOMAIN = getattr(settings, "FULL_DOMAIN", "http://localhost:8000").rstrip("/")

# --- SEO defaults ---------------------------------------------------------
DEFAULT_META_DESCRIPTION = (
    "Issa Abdulsalam Opeyemi is a backend developer working with Django, "
    "Django REST Framework, PostgreSQL, Flutter, and Go. Explore projects, "
    "the build feed, and the CV."
)

FEED_DESCRIPTION = (
    "Short updates on what I am building, learning, and shipping: Django, "
    "APIs, Flutter, Go, and the occasional hard-won lesson."
)

# --- Social / contact links ----------------------------------------------
SOCIAL_LINKS = {
    "email": "lastissa11@gmail.com",
    "github": "https://github.com/Lastissa",
    "linkedin": "https://linkedin.com/in/lastissa",
    "twitter": "https://x.com/lastissa",
    "whatsapp": "https://wa.me/2348113577875",
}

# --- Education ------------------------------------------------------------
EDUCATION = [
    {
        "institution": "Federal University of Ilorin, Kwara State",
        "credential": "B.Sc. Computer Science",
        "status": "In progress",
        "period": "Current",
    },
]

# --- Skills, grouped for the landing page ---------------------------------
SKILLS = {
    "Backend": ["Python", "Django", "Django REST Framework", "PostgreSQL", "SQL"],
    "Mobile": ["Flutter"],
    "Deployment": ["Render", "WhiteNoise", "Gunicorn"],
    "Currently exploring": [
        "Go for concurrency and compiled backend work",
        "Redis and caching strategy",
    ],
}

# --- CV files -------------------------------------------------------------
# Fallback used before the owner uploads a CV through the dashboard.
CV_FILENAME = "issa-abdulsalam-opeyemi-cv.pdf"
CV_DISPLAY_NAME = "Issa Abdulsalam Opeyemi - CV.pdf"
