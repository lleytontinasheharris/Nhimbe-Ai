"""Knowledge Base models - Articles, Categories, and Ratings"""

from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.db.models import Avg


class ArticleCategory(models.Model):
    """Categories for knowledge base articles"""

    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(max_length=300, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name_plural = 'Article Categories'
        ordering = ['order', 'name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def article_count(self):
        return self.articles.filter(is_published=True).count()


class Article(models.Model):
    """Knowledge base articles"""

    DIFFICULTY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    summary = models.TextField(max_length=300, help_text="Brief description shown in listings")
    content = models.TextField(help_text="Full article content. You can use HTML for formatting.")
    category = models.ForeignKey(
        ArticleCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='articles'
    )
    
    # Author can be a user OR external source
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='articles',
        help_text="Leave blank if using external source"
    )
    
    # External source info (for articles not written by site users)
    external_author = models.CharField(
        max_length=200,
        blank=True,
        help_text="Name of external author or organization (e.g., 'FAO', 'AGRITEX')"
    )
    source_url = models.URLField(
        blank=True,
        help_text="Original source URL if applicable"
    )
    source_name = models.CharField(
        max_length=200,
        blank=True,
        help_text="Publication or website name (e.g., 'FAO Publications', 'Zimbabwe Farmer Magazine')"
    )
    
    difficulty = models.CharField(
        max_length=15,
        choices=DIFFICULTY_CHOICES,
        default='beginner'
    )
    featured_image = models.ImageField(
        upload_to='articles/images/',
        blank=True,
        null=True
    )
    
    # Downloadable file
    downloadable_file = models.FileField(
        upload_to='articles/downloads/',
        blank=True,
        null=True,
        help_text="PDF or document for farmers to download"
    )
    file_description = models.CharField(
        max_length=200,
        blank=True,
        help_text="E.g., 'Complete Maize Guide (PDF, 2.5MB)'"
    )
    
    # Status flags
    is_published = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    
    # Stats
    views = models.PositiveIntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_featured', '-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Article.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def increment_views(self):
        self.views += 1
        self.save(update_fields=['views'])

    def get_author_display(self):
        """Returns the display name for the author"""
        if self.author:
            return self.author.get_full_name() or self.author.username
        elif self.external_author:
            return self.external_author
        return "Nhimbe AI Team"

    def get_source_display(self):
        """Returns source info for external articles"""
        if self.source_name:
            return self.source_name
        return None

    def average_rating(self):
        """Get the average rating for this article"""
        avg = self.ratings.aggregate(Avg('score'))['score__avg']
        return round(avg, 1) if avg else None

    def rating_count(self):
        """Get total number of ratings"""
        return self.ratings.count()

    def user_rating(self, user):
        """Get a specific user's rating for this article"""
        if user.is_authenticated:
            rating = self.ratings.filter(user=user).first()
            return rating.score if rating else None
        return None


class ArticleRating(models.Model):
    """User ratings for articles"""

    SCORE_CHOICES = [
        (1, '1 - Not Helpful'),
        (2, '2 - Somewhat Helpful'),
        (3, '3 - Helpful'),
        (4, '4 - Very Helpful'),
        (5, '5 - Extremely Helpful'),
    ]

    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name='ratings'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='article_ratings'
    )
    score = models.PositiveSmallIntegerField(choices=SCORE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['article', 'user']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} rated {self.article.title}: {self.score}/5"