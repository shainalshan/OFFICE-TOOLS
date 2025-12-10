from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count
from .models import Ticket
from .forms import TicketForm
from core.decorators import check_tool_access

@login_required
@check_tool_access('ticketing') # Assuming 'ticketing' slug for tool
def create_ticket(request):
    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.user = request.user
            ticket.save()
            messages.success(request, f'Ticket {ticket.ticket_id} created successfully.')
            return redirect('my_tickets')
    else:
        form = TicketForm()
    return render(request, 'tickets/create_ticket.html', {'form': form})

@login_required
@check_tool_access('ticketing')
def my_tickets(request):
    # Hide completed tickets older than 24 hours
    cutoff_time = timezone.now() - timedelta(hours=24)
    
    tickets = Ticket.objects.filter(user=request.user)
    
    # Exclude old completed tickets
    visible_tickets = []
    for ticket in tickets:
        if ticket.status == 'COMPLETED':
            if ticket.completed_at and ticket.completed_at > cutoff_time:
                visible_tickets.append(ticket)
        else:
            visible_tickets.append(ticket)
            
    # Sort by created desc
    visible_tickets.sort(key=lambda x: x.created_at, reverse=True)
            
    return render(request, 'tickets/my_tickets.html', {'tickets': visible_tickets})

@user_passes_test(lambda u: u.is_superuser)
def admin_ticket_panel(request):
    # Filter handling
    status_filter = request.GET.get('status')
    priority_filter = request.GET.get('priority')
    
    tickets = Ticket.objects.all().order_by('-created_at')
    
    if status_filter:
        tickets = tickets.filter(status=status_filter)
    if priority_filter:
        tickets = tickets.filter(priority=priority_filter)
        
    if request.method == 'POST':
        ticket_id = request.POST.get('ticket_id')
        new_status = request.POST.get('new_status')
        
        ticket = get_object_or_404(Ticket, id=ticket_id)
        ticket.status = new_status
        ticket.save()
        messages.success(request, f'Ticket {ticket.ticket_id} updated to {new_status}.')
        return redirect('admin_ticket_panel')
        
    return render(request, 'tickets/admin_panel.html', {
        'tickets': tickets,
        'status_filter': status_filter,
        'priority_filter': priority_filter
    })

@user_passes_test(lambda u: u.is_superuser)
def ticket_reports(request):
    # Aggregate stats
    total_tickets = Ticket.objects.count()
    status_counts = Ticket.objects.values('status').annotate(count=Count('status'))
    priority_counts = Ticket.objects.values('priority').annotate(count=Count('priority'))
    
    # Helper to dict
    status_dict = {item['status']: item['count'] for item in status_counts}
    priority_dict = {item['priority']: item['count'] for item in priority_counts}
    
    context = {
        'total': total_tickets,
        'status_counts': status_dict,
        'priority_counts': priority_dict
    }
    return render(request, 'tickets/reports.html', context)
