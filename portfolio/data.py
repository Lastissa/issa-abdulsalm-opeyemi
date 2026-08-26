"""
portfolio/data.py

Static project data. No database, no admin, no migrations -- add a new
project by adding a dict to PROJECTS below and redeploying. See
workflow.md, decision P1, for why this is a plain Python file instead
of a Django model.

Fields:
    slug        -- used for the in-page anchor (/projects/#slug) so
                   individual projects are linkable and crawlable.
    name        -- project name.
    status      -- one of: "Live", "Completed", "In progress", "Archived"
                   Purely descriptive, drives the small status pill in
                   the UI. Doesn't have to match the list above exactly,
                   keep it short (1-2 words).
    summary     -- one-line description, used in <meta> and card preview.
    description -- longer paragraph, used in the expanded card body.
    stack       -- list of strings, rendered as tags.
    repo_url    -- GitHub (or other) repository link. "" to hide.
    live_url    -- deployed / downloadable artifact link. "" to hide.
    live_label  -- text on the live/download button, e.g. "Live demo",
                   "Download APK". Only used if live_url is set.
"""

PROJECTS = [
    {
        "slug": "discipline-and-streak",
        "name": "Discipline & Streak",
        "status": "Live",
        "summary": (
            "Django web app that tracks discipline and commitment streaks "
            "with a built-in reminder system."
        ),
        "description": (
            "A habit and discipline tracker built on Django with a "
            "server-rendered HTML/CSS/JS frontend. Ships with full "
            "authentication and permissions, an inbuilt reminder system, "
            "and a blog section. Hardened against CSRF and SQL injection "
            "as a deliberate exercise in Django security fundamentals, "
            "not an afterthought."
        ),
        "stack": ["Django", "HTML", "CSS", "JavaScript", "Auth & Permissions", "VAPID enabled"],
        "repo_url": "https://github.com/Lastissa/STREAK-and-DISCIPLINE",
        "live_url": "https://discipline-hu97.onrender.com/",
        "live_label": "Live demo",
    },
    {
        "slug": "httpchat",
        "name": "httpChat",
        "status": "In progress",
        "summary": (
            "HTTP-based real-time chat and news platform built on Django, "
            "optimised for time-to-interactive."
        ),
        "description": (
            "An HTTP-based chat and news application, still under active "
            "development. Authentication is in place and streaming "
            "responses are used for real-time delivery over plain HTTP. "
            "Primary focus of this project is performance -- specifically "
            "cutting down time-to-interactive (TTI) on a content-heavy "
            "streaming interface."
        ),
        "stack": ["Django", "HTTP Streaming", "Auth", "Performance / TTI"],
        "repo_url": "https://github.com/Lastissa/httpChat",
        "live_url": "https://httpchat.onrender.com/",
        "live_label": "Live demo",
    },
    {
        "slug": "school-management-api",
        "name": "School Management API",
        "status": "For sale",
        "summary": (
            "Data-heavy REST API for school management with role-based "
            "authentication and permissions."
        ),
        "description": (
            "A REST API built with Django REST Framework around "
            "role-based authentication and permissions for a school "
            "management system -- students, staff, and administrative "
            "data flows. Multitenancy is the next planned addition, "
            "aimed at turning this into a resellable SaaS-style product."
        ),
        "stack": ["Django", "Django REST Framework", "SQL", "RBAC"],
        "repo_url": "https://github.com/Lastissa/school-management-system-API",
        "live_url": "",
        "live_label": "",
    },
    {
        "slug": "lecture-tracker",
        "name": "Lecture Tracker",
        "status": "Functional (Android)",
        "summary": (
            "Android app for lecture tracking and analysis, built with "
            "Flutter and a Django REST Framework backend."
        ),
        "description": (
            "A mobile lecture-tracking application for Android, with "
            "Flutter on the frontend and Django REST Framework powering "
            "the API and analysis behind it. The core tracking features "
            "are fully functional; the reminder feature is currently "
            "disabled due to a dependency-version issue rather than a "
            "design flaw."
        ),
        "stack": ["Flutter", "Django REST Framework", "Android", "Analysis"],
        "repo_url": "https://github.com/Lastissa/lectureTrackerFrontend",
        "live_url": "https://drive.google.com/file/d/103_BUoNOauouN3Myz8eAe9IiPXZo1siB/view?usp=sharing",
        "live_label": "Download APK",
    },
    {
        "slug": "photo-compressor",
        "name": "Photo Compressor",
        "status": "Completed",
        "summary": (
            "CLI Python tool for adjusting image quality and size with "
            "raw quality-control access."
        ),
        "description": (
            "A command-line Python executable for compressing images "
            "while giving the user raw, direct control over the "
            "quality/size trade-off, instead of hiding it behind a "
            "single 'compress' button."
        ),
        "stack": ["Python", "CLI", "Image Processing"],
        "repo_url": "https://github.com/Lastissa/photo-compressor",
        "live_url": "",
        "live_label": "",
    },
    {
        "slug": "school-project",
        "name": "School Coursework Suite",
        "status": "Actively maintained",
        "summary": (
            "Coursework and assignments built with a team, including a "
            "scientific calculator and a CLI-based GUI exam simulator."
        ),
        "description": (
            "A collection of lecturer-assigned coursework handled with a "
            "team, including a scientific calculator with full exception "
            "handling and a exam simulator with a GUI, both written "
            "entirely in Python with zero external dependencies and run "
            "from the command line. The codebase is deliberately well "
            "documented so it stays modifiable, and it still receives "
            "updates."
        ),
        "stack": ["Python", "CLI", "GUI", "Exception Handling"],
        "repo_url": "https://github.com/Lastissa/school_project",
        "live_url": "",
        "live_label": "",
    },
]
