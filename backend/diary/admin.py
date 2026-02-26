from django.contrib import admin
from .models import User, Category, Mood, DiaryEntry


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('telegram_id', 'username', 'created_at')
    search_fields = ('telegram_id', 'username')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Mood)
class MoodAdmin(admin.ModelAdmin): 
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(DiaryEntry)
class DiaryEntryAdmin(admin.ModelAdmin):
    list_display = ('user', 'category', 'mood', 'sleep_quality', 'physical_condition', 'content', 'created_at')
    search_fields = ('user__username', 'content')
    list_filter = ('category', 'mood', 'created_at')
    ordering = ('-created_at',)


