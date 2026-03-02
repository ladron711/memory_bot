from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class User(models.Model):
    telegram_id = models.BigIntegerField(unique=True)
    username = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.username or 'NoUserName'} ({self.telegram_id})"
    
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return self.name
    
class Mood(models.Model):
    name = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return self.name

class DiaryEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='diary_entries')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='diary_entries')
    mood = models.ForeignKey(Mood, on_delete=models.SET_NULL, null=True, related_name='diary_entries')
    physical_condition = models.TextField(null=True, blank=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Entry by {self.user} on {self.created_at:%Y-%m-%d %H:%M}"

