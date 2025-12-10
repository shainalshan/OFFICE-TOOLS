from django.contrib import admin
from .models import Ticket

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('ticket_id', 'user', 'priority', 'status', 'created_at')
    list_filter = ('status', 'priority')
    search_fields = ('ticket_id', 'user__username', 'issue')
    readonly_fields = ('ticket_id', 'created_at', 'updated_at', 'completed_at')
