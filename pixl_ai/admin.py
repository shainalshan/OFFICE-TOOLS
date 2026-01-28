from django.contrib import admin
from .models import AI_KnowledgeBase, Chat_Log

@admin.register(AI_KnowledgeBase)
class AI_KnowledgeBaseAdmin(admin.ModelAdmin):
    list_display = ('topic', 'access_level', 'is_active')
    list_filter = ('access_level', 'is_active')
    search_fields = ('topic', 'content')

@admin.register(Chat_Log)
class Chat_LogAdmin(admin.ModelAdmin):
    list_display = ('user', 'question', 'timestamp')
    list_filter = ('timestamp', 'user')
    search_fields = ('user__username', 'question', 'answer')
    readonly_fields = ('timestamp',)
