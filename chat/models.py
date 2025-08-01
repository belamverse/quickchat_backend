from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

# Create your models here.
class Room(models.Model):
    name = models.CharField(max_length=100, unique=True, null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True,null=False, blank=False)

    def __str__(self):
        return self.name
    
class ChatMessage(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='messages', null=True,blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messages', null=True, blank=True)
    message = models.TextField(null=False, blank=False)
    timestamp = models.DateTimeField(auto_now_add=True,null=False, blank=False)

    def __str__(self):
        return f"{self.user}: {self.message[:50]}..."
