from django.conf import settings


# --- Identity -----------------------------------------------------------
FULL_NAME = "Issa Abdulsalam Opeyemi"
SHORT_NAME = "Issa Abdulsalam"
SITE_TITLE = "Issa Abdulsalam Opeyemi"
ROLE_TITLE = "Backend Developer working towards Software Development"

TAGLINE = (
    "Driven to building maintainable systems."
    "Working with logic is my core in addition, i can pick up UI when the need comes, "
    ""
)

# --- Canonical domain -----------------------------------------------------
#Every canonical/OG/sitemap URL in
# this project is derived from this single value.
SITE_DOMAIN = getattr(settings, 'FULL_DOMAIN', 'http:localhost:8000')

# --- SEO defaults (used as fallback meta description/keywords) -----------
DEFAULT_META_DESCRIPTION = (
    "Issa Abdulsalam Opeyemi is a backend developer specialising in "
    "Django and Django REST Framework, with mobile app experience in "
    "Flutter and growing expertise in Go for high-concurrency backend "
    "systems. Explore projects, CV, and skills."
)

DEFAULT_META_KEYWORDS = [
    "Issa Abdulsalam Opeyemi",
    "Issa Abdulsalam",
    "Backend Developer",
    "Django Developer",
    "Django REST Framework Developer",
    "Python Backend Engineer",
    "Flutter Mobile Developer",
    "Go Backend Developer",
    "Software Developer Nigeria",
    "Federal University of Ilorin Computer Science",
]

# --- Social / contact links ----------------------------------------------

SOCIAL_LINKS = {
    "email": "lastissa11@gmail.com",
    "github": "https://github.com/Lastissa",
    "linkedin": "https://linkedin.com/in/lastissa",
    "twitter": "https://x.com/lastissa",
    "whatsapp":  "https://wa.me/2348113577875"
}

# --- Education -------------------------------------------------------------
EDUCATION = [
    {
        "institution": "Federal University of Ilorin, Kwara State",
        "credential": "B.Sc. Computer Science",
        "status": "In progress",
        "period": "Current",
    },
]

# --- Skills, grouped for the landing page ----------------------------------
SKILLS = {
    "Backend": ["Python", "Django", "Django REST Framework", "SQL"],
    "Mobile": ["Flutter"],
    "Deployment": ["Deployment / Render"],
    "Currently exploring": [
        "Go -- chasing the concurrency Django can't natively give me, "
        "and picking up a compiled language for backend work",
    ],
}

# --- CV files ---------------------------------------------------------------

CV_FILENAME = "issa-abdulsalam-opeyemi-cv.pdf"
CV_DISPLAY_NAME = "Issa Abdulsalam Opeyemi - CV.pdf"
