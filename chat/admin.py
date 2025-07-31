from django.contrib import admin

# Register your models here.
# chat/admin.py
from django.contrib import admin
from .models import Room, ChatMessage

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('room', 'user', 'timestamp')
    list_filter = ('room', 'user')