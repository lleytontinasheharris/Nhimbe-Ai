"""Knowledge Base admin configuration"""

from django.contrib import admin
from .models import ArticleCategory, Article, ArticleRating


@admin.register(ArticleCategory)
class ArticleCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'order', 'article_count']
    list_editable = ['order']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name', 'description']


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'difficulty', 'is_published', 'is_featured', 'views', 'average_rating', 'created_at']
    list_filter = ['category', 'difficulty', 'is_published', 'is_featured', 'created_at']
    list_editable = ['is_published', 'is_featured']
    search_fields = ['title', 'summary', 'content']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['views', 'created_at', 'updated_at']
    
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'category', 'author')
        }),
        ('Content', {
            'fields': ('summary', 'content', 'featured_image')
        }),
        ('Downloadable Resource', {
            'fields': ('downloadable_file', 'file_description'),
            'classes': ('collapse',)
        }),
        ('Settings', {
            'fields': ('difficulty', 'is_published', 'is_featured')
        }),
        ('Statistics', {
            'fields': ('views', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def average_rating(self, obj):
        avg = obj.average_rating()
        return f"{avg}/5" if avg else "No ratings"
    average_rating.short_description = 'Rating'


@admin.register(ArticleRating)
class ArticleRatingAdmin(admin.ModelAdmin):
    list_display = ['article', 'user', 'score', 'created_at']
    list_filter = ['score', 'created_at']
    search_fields = ['article__title', 'user__username']
    readonly_fields = ['created_at', 'updated_at']