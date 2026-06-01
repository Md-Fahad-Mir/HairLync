from django.db import models
from django.conf import settings


class EducationCategory(models.Model):
    """Categories for educational content."""
    class Meta:
        verbose_name = 'Education Category'
        verbose_name_plural = 'Education Categories'
        ordering = ['name']

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, default='')
    icon = models.CharField(max_length=50, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class EducationalContent(models.Model):
    """Educational content (videos, guides) for professionals."""
    class Meta:
        verbose_name = 'Educational Content'
        verbose_name_plural = 'Educational Contents'
        ordering = ['-created_at']

    CONTENT_TYPE_CHOICES = [
        ('video', 'Video'),
        ('guide', 'Guide'),
        ('article', 'Article'),
        ('tutorial', 'Tutorial'),
    ]

    DIFFICULTY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]

    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    category = models.ForeignKey(EducationCategory, on_delete=models.SET_NULL, null=True, related_name='contents')
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPE_CHOICES, default='article')
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='beginner')
    description = models.TextField(blank=True, default='')
    body = models.TextField(blank=True, default='', help_text='Full content body (for articles/guides)')
    video_url = models.URLField(blank=True, default='', help_text='Video URL (YouTube, Vimeo, etc.)')
    thumbnail = models.ImageField(upload_to='education/thumbnails/', blank=True, null=True)
    duration_minutes = models.PositiveIntegerField(default=0, help_text='Duration for videos in minutes')
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='authored_content'
    )
    is_premium = models.BooleanField(default=True, help_text='Requires active subscription to access')
    is_published = models.BooleanField(default=False)
    view_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
