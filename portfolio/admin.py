from django.contrib import admin

from .models import CVVersion, FeedPost, PageView, Visitor


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
