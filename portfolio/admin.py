from django.contrib import admin

from .models import (
    CVVersion,
    EducationEntry,
    FeedPost,
    LoginPoint,
    NowItem,
    PageContent,
    PageView,
    Principle,
    Project,
    ProjectTechnology,
    SiteSettings,
    Skill,
    SkillGroup,
    SocialLink,
    Visitor,
)


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ("full_name", "role_title", "toast_position", "updated_at")
    fieldsets = (
        (
            "Identity",
            {
                "fields": (
                    "full_name",
                    "short_name",
                    "initials",
                    "role_title",
                    "location",
                    "city",
                    "country_code",
                    "tagline",
                    "availability",
                    "email",
                    "avatar_url",
                )
            },
        ),
        (
            "SEO",
            {
                "fields": (
                    "site_title",
                    "default_meta_description",
                    "feed_description",
                    "keywords",
                )
            },
        ),
        (
            "Landing page",
            {
                "fields": (
                    "hero_eyebrow",
                    "hero_heading",
                    "hero_accent",
                    "hero_lead",
                    "focus_summary",
                    "stack_summary",
                    "years_experience",
                    "projects_delivered",
                    "about_heading",
                    "about_body",
                    "contact_heading",
                    "contact_body",
                    "footer_note",
                )
            },
        ),
        (
            "Interface",
            {
                "fields": (
                    "cv_display_name",
                    "toast_position",
                    "default_theme",
                )
            },
        ),
    )

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(PageContent)
class PageContentAdmin(admin.ModelAdmin):
    list_display = ("get_key_display", "heading", "is_active", "updated_at")
    list_editable = ("is_active",)
    search_fields = ("heading", "intro")


class SkillInline(admin.TabularInline):
    model = Skill
    extra = 1
    ordering = ("order", "name")


@admin.register(SkillGroup)
class SkillGroupAdmin(admin.ModelAdmin):
    list_display = ("name", "order", "is_active")
    list_editable = ("order", "is_active")
    inlines = [SkillInline]


@admin.register(SocialLink)
class SocialLinkAdmin(admin.ModelAdmin):
    list_display = ("label", "platform", "url", "order", "is_active")
    list_editable = ("order", "is_active")


@admin.register(EducationEntry)
class EducationEntryAdmin(admin.ModelAdmin):
    list_display = ("credential", "institution", "period", "order", "is_active")
    list_editable = ("order", "is_active")


@admin.register(Principle)
class PrincipleAdmin(admin.ModelAdmin):
    list_display = ("title", "order", "is_active")
    list_editable = ("order", "is_active")


@admin.register(NowItem)
class NowItemAdmin(admin.ModelAdmin):
    list_display = ("text", "order", "is_active")
    list_editable = ("order", "is_active")


@admin.register(LoginPoint)
class LoginPointAdmin(admin.ModelAdmin):
    list_display = ("text", "icon", "order", "is_active")
    list_editable = ("order", "is_active")


class ProjectTechnologyInline(admin.TabularInline):
    model = ProjectTechnology
    extra = 1
    ordering = ("order", "name")


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "status",
        "featured",
        "is_published",
        "order",
        "updated_at",
    )
    list_editable = ("featured", "is_published", "order")
    list_filter = ("status", "featured", "is_published")
    search_fields = ("name", "summary", "description")
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("created_at", "updated_at")
    inlines = [ProjectTechnologyInline]
    fieldsets = (
        (
            "Basics",
            {
                "fields": (
                    "name",
                    "slug",
                    "status",
                    "summary",
                    "description",
                    "focus",
                )
            },
        ),
        (
            "Case study",
            {
                "fields": (
                    "role",
                    "year",
                    "project_type",
                    "live_url",
                    "live_label",
                    "repo_url",
                    "embeddable",
                    "preview_note",
                )
            },
        ),
        (
            "Publishing",
            {
                "fields": (
                    "featured",
                    "is_published",
                    "order",
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )


@admin.register(FeedPost)
class FeedPostAdmin(admin.ModelAdmin):
    list_display = ("excerpt", "author", "is_published", "created_at")
    list_filter = ("is_published", "created_at")
    search_fields = ("content", "author__username")
    date_hierarchy = "created_at"
    readonly_fields = ("created_at", "updated_at")


@admin.register(CVVersion)
class CVVersionAdmin(admin.ModelAdmin):
    list_display = ("original_name", "is_active", "uploaded_by", "uploaded_at")
    list_filter = ("is_active", "uploaded_at")
    search_fields = ("original_name",)
    readonly_fields = ("uploaded_at",)

    def save_model(self, request, obj, form, change):
        if obj.is_active:
            CVVersion.objects.exclude(pk=obj.pk).update(is_active=False)
        if not obj.uploaded_by_id:
            obj.uploaded_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(PageView)
class PageViewAdmin(admin.ModelAdmin):
    list_display = ("path", "date", "views")
    list_filter = ("date",)
    search_fields = ("path",)
    date_hierarchy = "date"


@admin.register(Visitor)
class VisitorAdmin(admin.ModelAdmin):
    list_display = (
        "short_hash",
        "views",
        "last_path",
        "referrer",
        "last_seen",
    )
    search_fields = ("visitor_hash", "last_path", "referrer")
    readonly_fields = (
        "visitor_hash",
        "first_seen",
        "last_seen",
        "views",
        "last_path",
        "user_agent",
        "referrer",
    )

    def has_add_permission(self, request):
        return False
