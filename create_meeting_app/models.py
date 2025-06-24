# 1. MODELS - create_meeting_app/models.py
from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User

class Meeting(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='meetings')
    name = models.CharField(max_length=100)
    bot_name = models.CharField(max_length=100)
    meeting_link = models.URLField()
    join_time = models.TimeField(null=True, blank=True)
    joined = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.bot_name})"

    def get_absolute_url(self):
        return reverse('meeting_page', kwargs={'meeting_id': self.pk})

class Transcript(models.Model):
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, related_name="transcripts")
    text = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

class Screenshot(models.Model):
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, related_name="screenshots")
    image_path = models.CharField(max_length=255)
    created = models.DateTimeField(auto_now_add=True)