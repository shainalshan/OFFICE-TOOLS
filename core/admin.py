from django.contrib import admin
from .models import Tool, UserToolAccess

@admin.register(Tool)
class ToolAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(UserToolAccess)
class UserToolAccessAdmin(admin.ModelAdmin):
    list_display = ('user',)
    filter_horizontal = ('tools',)
