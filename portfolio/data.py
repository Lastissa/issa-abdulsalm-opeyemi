PROJECTS = [
    {
        "slug": "abureport",
        "name": "Abureport",
        "status": "Live",
        "status_class": "live",
        "summary": (
            "A full-stack news platform with role-aware pages and a "
            "content workflow that does not need code changes."
        ),
        "description": (
            "A news publishing platform with several pages, all verified "
            "against failure and backed by heavy data. It handles that load "
            "with deliberate caching and cache invalidation so readers do not "
            "see stale content. Most editorial changes can be made without "
            "rewriting code."
        ),
        "stack": [
            "Django",
            "HTML",
            "CSS",
            "JavaScript",
            "Auth & Permissions",
            "PostgreSQL",
        ],
        "live_url": "https://abureport.com.ng",
        "live_label": "Visit live site",
        "repo_url": "",
        "embeddable": True,
        "featured": True,
    },
    {
        "slug": "discipline-and-streak",
        "name": "Discipline & Streak",
        "status": "Live",
        "status_class": "live",
        "summary": (
            "A Django app that tracks discipline and commitment streaks "
            "with a built-in reminder system."
        ),
        "description": (
            "A habit and discipline tracker built on Django with a "
            "server-rendered HTML, CSS, and JavaScript frontend. It ships "
            "with full authentication and permissions, an inbuilt reminder "
            "system, and a blog section. The build was also an exercise in "
            "Django security fundamentals, including CSRF and SQL injection "
            "hardening."
        ),
        "stack": [
            "Django",
            "HTML",
            "CSS",
            "JavaScript",
            "Auth & Permissions",
            "VAPID",
            "PostgreSQL",
        ],
        "repo_url": "https://github.com/Lastissa/STREAK-and-DISCIPLINE",
        "live_url": "https://discipline-hu97.onrender.com/",
        "live_label": "Live demo",
        "embeddable": True,
        "featured": True,
    },
    {
        "slug": "httpchat",
        "name": "httpChat",
        "status": "In progress",
        "status_class": "progress",
        "summary": (
            "An HTTP-based real-time chat and news platform optimised for "
            "time-to-interactive."
        ),
        "description": (
            "A chat and news application still under active development. "
            "Authentication is in place, and responses are used for real-time "
            "delivery over plain HTTP. The main focus is performance: cutting "
            "time-to-interactive on a content-heavy streaming interface while "
            "pushing HTTP further than it is usually asked to go. Video "
            "channels are in scope for a later iteration."
        ),
        "stack": [
            "Django",
            "Auth",
            "Performance / TTI",
            "HTML",
            "CSS",
            "Vanilla JS",
        ],
        "repo_url": "https://github.com/Lastissa/httpChat",
        "live_url": "https://httpchat.onrender.com/",
        "live_label": "Live demo",
        "embeddable": True,
        "featured": True,
    },
    {
        "slug": "school-management-api",
        "name": "School Management API",
        "status": "For sale",
        "status_class": "sale",
        "summary": (
            "A data-heavy REST API for school management with role-based "
            "authentication and permissions."
        ),
        "description": (
            "A REST API built with Django REST Framework around role-based "
            "authentication and permissions for a school management system. "
            "The current scope covers six roles across administration, "
            "management, parents, teaching staff, and non-teaching staff. "
            "Multitenancy is the next planned addition after the first MVP, "
            "with the goal of turning it into a multi-school SaaS-style product."
        ),
        "stack": ["Django", "Django REST Framework", "SQL", "RBAC", "Redis"],
        "repo_url": "https://github.com/Lastissa/school-management-system-API",
        "live_url": "",
        "live_label": "",
        "embeddable": False,
        "featured": False,
    },
    {
        "slug": "lecture-tracker",
        "name": "Lecture Tracker",
        "status": "Functional (Android)",
        "status_class": "functional",
        "summary": (
            "An Android app for lecture tracking and analysis, built with "
            "Flutter and a Django REST Framework backend."
        ),
        "description": (
            "A mobile lecture-tracking application for Android, with Flutter "
            "on the frontend and Django REST Framework powering the API and "
            "the analysis behind it. The core tracking features are fully "
            "functional. The reminder feature is currently disabled because "
            "of a dependency-version issue, not a design flaw."
        ),
        "stack": ["Flutter", "Django REST Framework", "Android", "Analysis"],
        "repo_url": "https://github.com/Lastissa/lectureTrackerFrontend",
        "live_url": (
            "https://drive.google.com/file/d/103_BUoNOauouN3Myz8eAe9IiPXZo1siB/view"
        ),
        "live_label": "Download APK",
        "embeddable": False,
        "featured": True,
    },
    {
        "slug": "photo-compressor",
        "name": "Photo Compressor",
        "status": "Completed",
        "status_class": "completed",
        "summary": (
            "A command-line Python tool for adjusting image quality and size "
            "with direct quality control."
        ),
        "description": (
            "A command-line Python executable for compressing images while "
            "giving the user raw control over the quality and size trade-off, "
            "instead of hiding it behind a single compress command. Setup "
            "instructions are included in the repository."
        ),
        "stack": ["Python", "CLI", "Image Processing"],
        "repo_url": "https://github.com/Lastissa/photo-compressor",
        "live_url": "",
        "live_label": "",
        "embeddable": False,
        "featured": False,
    },
    {
        "slug": "school-project",
        "name": "School Coursework Suite",
        "status": "Actively maintained",
        "status_class": "maintained",
        "summary": (
            "Coursework built with a team, including a scientific calculator "
            "and a CLI-based GUI exam simulator."
        ),
        "description": (
            "A collection of lecturer-assigned coursework handled with a team, "
            "including a scientific calculator with full exception handling and "
            "an exam simulator with a GUI. Both are written entirely in Python "
            "with zero external dependencies and run from the command line. "
            "The codebase is deliberately documented so it stays modifiable, "
            "and it still receives updates."
        ),
        "stack": ["Python", "CLI", "GUI", "Exception Handling"],
        "repo_url": "https://github.com/Lastissa/school_project",
        "live_url": "",
        "live_label": "",
        "embeddable": False,
        "featured": False,
    },
]


def get_project(slug):
    return next((project for project in PROJECTS if project["slug"] == slug), None)


def featured_projects(limit=3):
    projects = [project for project in PROJECTS if project.get("featured")]
    return projects[:limit] or PROJECTS[:limit]
