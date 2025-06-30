from django.contrib import admin
from .models import Work, Comment

@admin.register(Work)
class WorkAdmin(admin.ModelAdmin):
    list_display = ('title', 'genre', 'author', 'published_at', 'rating')
    search_fields = ('title', 'author__username', 'genre')
    list_filter = ('genre', 'published_at')
    ordering = ('-published_at',)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'work', 'created_at')
    search_fields = ('user__username', 'work__title', 'content')
    list_filter = ('created_at',)
    ordering = ('-created_at',)
