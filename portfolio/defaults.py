"""Seed content for a fresh database.

These values are only used by ``seed_content`` (and the post-migrate hook).
The public site always reads the database.
"""

SITE = {
    "full_name": "Full Name",
    "short_name": "Short Name",
    "initials": "In",
    "role_title": "Role Title",
    "location": "Location",
    "city": "City",
    "country_code": "NG",
    "tagline": (
        "What do i do."
    ),
    "availability": "Avaability",
    "email": "lastissa11@gmail.com",
    "site_title": "Site Title",
    "default_meta_description": (
        "Issa Abdulsalam Opeyemi is a fullstack developer majoring in backend development working with Django, "
        "Django REST Framework, PostgreSQL, Flutter, html, htmx, css,vanilla js and Go. Explore projects, "
        "the build feed, and the CV."
    ),
    "feed_description": (
        "This is where i post Short updates on what I am building, learning, and deploying: Django, "
        "APIs, Flutter, Go, and the occasional hard-won lesson."
    ),
    "keywords": (
        "Django, Django REST Framework, PostgreSQL, Python, Flutter, Go, "
        "Backend Developer", "Fullstack Developer",
    ),
    "hero_eyebrow": "Hero Eyebrow",
    "hero_heading": "I build backends that stay",
    "hero_accent": "maintainable",
    "hero_lead": (
        "I am Issa Abdulsalam Opeyemi. I work with Django, Django REST "
        "Framework, PostgreSQL, Flutter, and Go. Based in Ilorin, Nigeria."
    ),
    "focus_summary": "Backend systems, APIs, and data-heavy products",
    "stack_summary": "Django, DRF, PostgreSQL, Flutter, Go",
    "years_experience": 3,
    "projects_delivered": 7,
    "about_heading": "How I work",
    "about_body": (
        "A product without findings is a product waiting to fail. I start by "
        "understanding the data, the constraints, and the failure cases, then "
        "choose the tool that fits the job."
    ),
    "contact_heading": "Have a backend problem worth solving?",
    "contact_body": (
        "Email is the fastest way to reach me. I also answer on WhatsApp and "
        "LinkedIn."
    ),
    "footer_note": (
        "Python, PostgreSQL,UI and a bias for maintainable systems."
    ),
    "avatar_url": "",
    "cv_display_name": "Issa Abdulsalam Opeyemi - CV.pdf",
    "toast_position": "top",
    "default_theme": "system",
}

PAGE_CONTENT = {
    "projects": {
        "eyebrow": "Project reviews",
        "heading": "Things I have built",
        "intro": (
            "Every project here started with a problem, a constraint, or a tool "
            "I wanted to understand properly. Open a case study for the full "
            "write-up and a live preview where one exists."
        ),
        "meta_description": (
            "Project write-ups by Issa Abdulsalam Opeyemi, a backend developer "
            "working with Django, Django REST Framework, PostgreSQL, Flutter, "
            "and Go. Each entry includes the stack, repository, and live link."
        ),
        "og_description": (
            "Backend and mobile projects built with Django, DRF, PostgreSQL, "
            "Flutter, and Go."
        ),
    },
    "feed": {
        "eyebrow": "The build feed",
        "heading": "Notes from the work",
        "intro": (
            "Short updates on what I am building, learning, and shipping. "
            "Publishing is limited to the owner; reading is open to everyone."
        ),
        "meta_description": (
            "Short updates on what I am building, learning, and shipping: "
            "Django, APIs, Flutter, Go, and the occasional hard-won lesson."
        ),
        "og_description": (
            "Build notes on Django, APIs, Flutter, Go, and maintainable systems."
        ),
    },
    "cv": {
        "eyebrow": "Curriculum vitae",
        "heading": "",
        "intro": "View it below, download the PDF, or open it in a new tab.",
        "meta_description": (
            "View or download the CV of Issa Abdulsalam Opeyemi, a backend "
            "developer working with Django, Django REST Framework, PostgreSQL, "
            "Flutter, and Go."
        ),
        "og_description": "View or download the CV of Issa Abdulsalam Opeyemi.",
    },
    "login": {
        "eyebrow": "Owner access",
        "heading": "Sign in to manage the site",
        "intro": (
            "Use your staff account to upload a CV, publish a post, or open the "
            "analytics dashboard."
        ),
        "meta_description": "Owner login for Issa Abdulsalam Opeyemi.",
        "og_description": "Owner login.",
    },
}

SOCIAL_LINKS = [
    {
        "platform": "github",
        "label": "GitHub",
        "url": "https://github.com/Lastissa",
        "handle": "@Lastissa",
        "order": 1,
    },
    {
        "platform": "linkedin",
        "label": "LinkedIn",
        "url": "https://linkedin.com/in/lastissa",
        "handle": "in/lastissa",
        "order": 2,
    },
    {
        "platform": "twitter",
        "label": "X / Twitter",
        "url": "https://x.com/lastissa",
        "handle": "@lastissa",
        "order": 3,
    },
    {
        "platform": "whatsapp",
        "label": "WhatsApp",
        "url": "https://wa.me/2348113577875",
        "handle": "+234 811 357 7875",
        "order": 4,
    },
    {
        "platform": "email",
        "label": "Email",
        "url": "mailto:lastissa11@gmail.com",
        "handle": "lastissa11@gmail.com",
        "order": 5,
    },
]

SKILL_GROUPS = [
    {
        "name": "Backend",
        "order": 1,
        "skills": ["Python", "Django", "Django REST Framework", "PostgreSQL", "SQL"],
    },
    {"name": "Mobile", "order": 2, "skills": ["Flutter"]},
    {"name": "Deployment", "order": 3, "skills": ["Render", "WhiteNoise", "Gunicorn"]},
    {
        "name": "Currently exploring",
        "order": 4,
        "skills": [
            "React - better code management",
            "Go - backend for speed and concurency",
        ],
    },
]

EDUCATION = [
    {
        "institution": "Federal University of Ilorin, Kwara State",
        "credential": "B.Sc. Computer Science",
        "status": "In progress",
        "period": "Current",
        "order": 1,
    },
]

PRINCIPLES = [
    {
        "title": "Research before building",
        "body": (
            "A product without findings is a product waiting to fail. I start by "
            "understanding the data, the limitations and the failure cases, then "
            "choose the tool that fits the job."
        ),
        "order": 1,
    },
    {
        "title": "Maintainability over cleverness",
        "body": (
            "Most of what I ship runs on Django and DRF because they are "
            "data-heavy, secure, and well supported. PostgreSQL is my default "
            "database. Flutter covers mobile and desktop from one codebase. Go is "
            "next, for its speed and concurrency model."
        ),
        "order": 2,
    },
    {
        "title": "Ship the failure cases",
        "body": (
            "Empty states, retries, cache invalidation, and permission edges are "
            "part of the build, not cleanup. If a path can fail, it gets a "
            "deliberate answer before release."
        ),
        "order": 3,
    },
]

NOW_ITEMS = [
    {"text": "Building and hardening Django backends", "order": 1},
    {"text": "Going deeper into Go for concurrency", "order": 2},
    {"text": "Documenting the work on the feed", "order": 3},
]

LOGIN_POINTS = [
    {
        "icon": "cv",
        "text": "Upload a new CV and keep older versions until you delete them.",
        "order": 1,
    },
    {
        "icon": "feed",
        "text": "Publish text posts with an external image URL.",
        "order": 2,
    },
    {
        "icon": "analytics",
        "text": "Read page views and visitor trends without a third-party tracker.",
        "order": 3,
    },
]

PROJECTS = [
    {
        "slug": "abureport",
        "name": "Abureport",
        "status": "live",
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
        "focus": (
            "Cache invalidation, role-aware pages, and an editorial workflow "
            "that lets the newsroom publish without waiting on a deploy."
        ),
        "role": "Full-stack build",
        "year": "2025",
        "project_type": "Web application",
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
        "preview_note": (
            "If the preview stays blank, the site may block embedding. Use the "
            "open-in-new-tab button in the browser bar."
        ),
        "order": 1,
    },
    {
        "slug": "discipline-and-streak",
        "name": "Discipline & Streak",
        "status": "live",
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
        "focus": (
            "Authentication, permission boundaries, reminder delivery, and "
            "closing the common Django security gaps before launch."
        ),
        "role": "Solo build",
        "year": "2025",
        "project_type": "Web application",
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
        "live_url": "https://dstrict.vercel.app/",
        "live_label": "Live demo",
        "embeddable": True,
        "featured": True,
        "preview_note": (
            "project maintance is not frequent",
        ),
        "order": 2,
    },
    {
        "slug": "httpchat",
        "name": "httpChat",
        "status": "progress",
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
        "focus": (
            "Streaming responses, time-to-interactive, and keeping a content-heavy "
            "interface usable on slow connections."
        ),
        "role": "Solo build",
        "year": "2026",
        "project_type": "Web application",
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
        "preview_note": (
            "The app is still in progress, so some routes may change between "
            "visits."
        ),
        "order": 3,
    },
    {
        "slug": "school-management-api",
        "name": "School Management API",
        "status": "sale",
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
        "focus": (
            "Modelling six distinct roles without leaking permissions, and "
            "keeping the API shape stable enough to add tenancy later."
        ),
        "role": "API design and build",
        "year": "2025",
        "project_type": "REST API",
        "stack": ["Django", "Django REST Framework", "SQL", "RBAC", "Redis"],
        "repo_url": "https://github.com/Lastissa/school-management-system-API",
        "live_url": "",
        "live_label": "",
        "embeddable": False,
        "featured": False,
        "preview_note": "",
        "order": 4,
    },
    {
        "slug": "lecture-tracker",
        "name": "Lecture Tracker",
        "status": "functional",
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
        "focus": (
            "A Flutter client backed by a DRF API, with the analysis layer kept "
            "separate from the mobile UI."
        ),
        "role": "Mobile and API build",
        "year": "2024",
        "project_type": "Application / download",
        "stack": ["Flutter", "Django REST Framework", "Android", "Analysis"],
        "repo_url": "https://github.com/Lastissa/lectureTrackerFrontend",
        "live_url": (
            "https://drive.google.com/file/d/103_BUoNOauouN3Myz8eAe9IiPXZo1siB/view"
        ),
        "live_label": "Download APK",
        "embeddable": False,
        "featured": True,
        "preview_note": "",
        "order": 5,
    },
    {
        "slug": "photo-compressor",
        "name": "Photo Compressor",
        "status": "completed",
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
        "focus": (
            "A small CLI surface, predictable flags, and a quality/size trade-off "
            "the user can actually steer."
        ),
        "role": "Solo build",
        "year": "2024",
        "project_type": "Command-line tool",
        "stack": ["Python", "CLI", "Image Processing"],
        "repo_url": "https://github.com/Lastissa/photo-compressor",
        "live_url": "",
        "live_label": "",
        "embeddable": False,
        "featured": False,
        "preview_note": "",
        "order": 6,
    },
    {
        "slug": "school-project",
        "name": "School Coursework Suite",
        "status": "maintained",
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
        "focus": (
            "Team delivery, exception handling, and keeping a dependency-free "
            "Python codebase readable enough to keep updating."
        ),
        "role": "Team build",
        "year": "2024",
        "project_type": "Command-line tool",
        "stack": ["Python", "CLI", "GUI", "Exception Handling"],
        "repo_url": "https://github.com/Lastissa/school_project",
        "live_url": "",
        "live_label": "",
        "embeddable": False,
        "featured": False,
        "preview_note": "",
        "order": 7,
    },
]
