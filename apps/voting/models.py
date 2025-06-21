from django.db import models
from django.conf import settings


class Vote(models.Model):
    """Model representing a vote for a time slot."""
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='votes'
    )
    timeslot = models.ForeignKey(
        'events.TimeSlot',
        on_delete=models.CASCADE,
        related_name='votes'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'timeslot']
        verbose_name = 'Vote'
        verbose_name_plural = 'Votes'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} voted for {self.timeslot}"
