from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta, datetime
from django.db.models import Count
from django.http import HttpResponse
from .models import Ticket
from .forms import TicketForm
from core.decorators import check_tool_access
import csv
import openpyxl
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

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
        
    search_query = request.GET.get('ticket_search')
    if search_query:
        tickets = tickets.filter(ticket_id__icontains=search_query)
        
    if request.method == 'POST':
        ticket_id = request.POST.get('ticket_id')
        new_status = request.POST.get('new_status')
        
        ticket = get_object_or_404(Ticket, id=ticket_id)
        
        # Update Status
        if new_status:
            ticket.status = new_status
            
        # Update Resolution
        resolution = request.POST.get('resolution')
        if resolution is not None:
             ticket.resolution = resolution
             
        ticket.save()
        messages.success(request, f'Ticket {ticket.ticket_id} updated successfully.')
        return redirect('admin_ticket_panel')
        
    return render(request, 'tickets/admin_panel_fixed.html', {
        'tickets': tickets,
        'status_filter': status_filter,
        'priority_filter': priority_filter
    })

@user_passes_test(lambda u: u.is_superuser)
def ticket_reports(request):
    # Date Filtering
    date_range = request.GET.get('date_range', 'all')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    tickets = Ticket.objects.all()
    
    if date_range == 'last_month':
        today = timezone.now().date()
        first = today.replace(day=1)
        last_month_end = first - timedelta(days=1)
        last_month_start = last_month_end.replace(day=1)
        tickets = tickets.filter(created_at__date__gte=last_month_start, created_at__date__lte=last_month_end)
    elif start_date and end_date:
        tickets = tickets.filter(created_at__date__range=[start_date, end_date])
        
    # Stats Calculation
    total_tickets = tickets.count()
    status_counts = tickets.values('status').annotate(count=Count('status'))
    priority_counts = tickets.values('priority').annotate(count=Count('priority'))
    
    # Export Logic
    export_type = request.GET.get('export')
    if export_type == 'excel':
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename=ticket_report_{timezone.now().date()}.xlsx'
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Tickets"
        
        # Headers
        headers = ['Ticket ID', 'User', 'Status', 'Priority', 'Created At', 'Issue', 'Resolution']
        ws.append(headers)
        
        for t in tickets:
            res = t.resolution if t.resolution else ""
            ws.append([t.ticket_id, t.user.username, t.status, t.priority, t.created_at.replace(tzinfo=None), t.issue, res])
            
        wb.save(response)
        return response
        
    elif export_type == 'pdf':
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename=ticket_report_{timezone.now().date()}.pdf'
        
        doc = SimpleDocTemplate(response, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()
        
        # Title
        elements.append(Paragraph("Ticket Analytic Report", styles['Title']))
        elements.append(Paragraph(f"Date: {timezone.now().date()}", styles['Normal']))
        elements.append(Paragraph(f"Total Tickets: {total_tickets}", styles['Normal']))
        elements.append(Spacer(1, 20))
        
        # Stats Table
        stat_data = [['Status', 'Count']]
        for s in status_dict:
            stat_data.append([s, status_dict[s]])
            
        t_stats = Table(stat_data, colWidths=[150, 50])
        t_stats.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(t_stats)
        elements.append(Spacer(1, 20))
        
        # Ticket List Table
        elements.append(Paragraph("Ticket Details:", styles['Heading2']))
        elements.append(Spacer(1, 10))
        
        # Columns: ID, User, Status, Resolution
        # We limit columns to fit on page
        ticket_data = [['ID', 'User', 'Status', 'Resolution']]
        for t in tickets:
            res = t.resolution if t.resolution else ""
            # Wrap text if needed? standard Table handles some, but long text might overflow.
            # Paragraphs inside cells handle wrapping.
            res_para = Paragraph(res, styles['BodyText'])
            ticket_data.append([t.ticket_id, t.user.username, t.status, res_para])
            
        # Table with auto-wrapping for resolution
        t_tickets = Table(ticket_data, colWidths=[80, 80, 80, 300])
        t_tickets.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'), # Align top for multi-line
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        
        elements.append(t_tickets)
        
        doc.build(elements)
        return response

    # Helper to dict
    status_dict = {item['status']: item['count'] for item in status_counts}
    priority_dict = {item['priority']: item['count'] for item in priority_counts}
    
    context = {
        'total': total_tickets,
        'status_counts': status_dict,
        'priority_counts': priority_dict,
        'start_date': start_date,
        'end_date': end_date,
        'date_range': date_range
    }
    return render(request, 'tickets/reports.html', context)
