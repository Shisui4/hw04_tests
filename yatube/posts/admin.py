from django.contrib import admin

from .models import Group, Post, Comment, Follow


class PostAdmin(admin.ModelAdmin):
    list_display = ("author", "text", "pub_date", "pk", "group")
    list_editable = ("group",)
    search_fields = ("text",)
    list_filter = ("pub_date",)
    empty_value_display = "-пусто-"


class GroupAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}
    list_display = ("title", "description")
    search_fields = ("description",)
    list_filter = ("title",)
    empty_value_display = "-пусто-"


class CommentAdmin(admin.ModelAdmin):
    list_display = ("post", "author", "text", "created", "pk")
    search_fields = ("author",)
    list_filter = ("text",)
    empty_value_display = "-пусто-"


class FollowAdmin(admin.ModelAdmin):
    list_display = ("user", "author")
    search_fields = ("author", "follower")
    empty_value_display = "-пусто-"


admin.site.register(Post, PostAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Follow, FollowAdmin)
