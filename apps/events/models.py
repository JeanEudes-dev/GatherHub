from django.db import models
from django.conf import settings
from django.utils.text import slugify


class Event(models.Model):
    """Model representing an event."""
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('locked', 'Locked'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_events'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Event'
        verbose_name_plural = 'Events'
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Event.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)


class TimeSlot(models.Model):
    """Model representing a time slot for an event."""
    
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='time_slots'
    )
    datetime = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['datetime']
        verbose_name = 'Time Slot'
        verbose_name_plural = 'Time Slots'
        unique_together = ['event', 'datetime']
    
    def __str__(self):
        return f"{self.event.title} - {self.datetime.strftime('%Y-%m-%d %H:%M')}"
