
content = """{% extends 'core/base.html' %}

{% block content %}
<div class="animate-fade-in">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem;">
        <h1 style="margin:0;">Ticket Admin Panel</h1>
        <a href="{% url 'ticket_reports' %}" class="btn-primary" style="width: auto; margin-top: 0; padding: 0.75rem 1.5rem; background: #64748b;">📊 View Reports</a>
    </div>

    <!-- Filters -->
    <div class="glass-container" style="padding: 1rem; margin-bottom: 2rem; display: flex; gap: 1rem; align-items: center;">
        <span style="font-weight: bold; color: var(--text-secondary);">Filter:</span>
        <a href="?" style="color: white; text-decoration: none; opacity: {% if not status_filter and not priority_filter %}1{% else %}0.6{% endif %};">All</a>
        <a href="?status=PENDING" style="color: white; text-decoration: none; opacity: {% if status_filter == 'PENDING' %}1{% else %}0.6{% endif %};">Pending</a>
        <a href="?status=IN_PROGRESS" style="color: white; text-decoration: none; opacity: {% if status_filter == 'IN_PROGRESS' %}1{% else %}0.6{% endif %};">In Progress</a>
        <a href="?priority=P1" style="color: #ef4444; text-decoration: none; opacity: {% if priority_filter == 'P1' %}1{% else %}0.6{% endif %}; font-weight: bold;">P1 Critical</a>

        <!-- Search -->
        <form method="get" style="margin-left: auto; display: flex; gap: 0.5rem;">
            <input type="text" name="ticket_search" placeholder="Search Ticket ID..." value="{{ request.GET.ticket_search|default:'' }}"
                   style="padding: 0.5rem; border-radius: 4px; border: 1px solid rgba(255,255,255,0.2); background: rgba(0,0,0,0.2); color: white;">
            <button type="submit" class="btn-primary" style="width: auto; padding: 0.5rem 1rem; font-size: 0.9rem;">Search</button>
        </form>
    </div>

    <!-- Ticket List -->
    <div class="glass-container" style="padding: 0;">
        <table style="width: 100%; border-collapse: collapse;">
            <thead>
                <tr style="text-align: left; border-bottom: 1px solid var(--glass-border);">
                    <th style="padding: 1rem;">ID</th>
                    <th style="padding: 1rem;">User</th>
                    <th style="padding: 1rem;">Priority</th>
                    <th style="padding: 1rem;">Issue</th>
                    <th style="padding: 1rem;">Status</th>
                    <th style="padding: 1rem;">Created</th>
                </tr>
            </thead>
            <tbody>
                {% for ticket in tickets %}
                <tr style="border-bottom: 1px solid rgba(255,255,255,0.05);">
                    <td style="padding: 1rem; font-weight: bold;">{{ ticket.ticket_id }}</td>
                    <td style="padding: 1rem;">{{ ticket.user.username }}</td>
                    <td style="padding: 1rem;">
                        <span class="dot-{{ ticket.priority }}">{{ ticket.get_priority_display }}</span>
                    </td>
                    <td style="padding: 1rem; max-width: 300px;">{{ ticket.issue|truncatechars:50 }}</td>
                    <td style="padding: 1rem;">
                        <!-- Status Changer Form -->
                         <form method="post" style="display: flex; gap: 0.5rem;">
                            {% csrf_token %}
                            <input type="hidden" name="ticket_id" value="{{ ticket.id }}">
                            <select name="new_status" onchange="this.form.submit()" style="padding: 0.25rem; font-size: 0.8rem; width: auto; background: rgba(0,0,0,0.3); border: 1px solid rgba(255,255,255,0.2);">
                                <option value="PENDING" {% if ticket.status == 'PENDING' %}selected{% endif %}>Pending</option>
                                <option value="IN_PROGRESS" {% if ticket.status == 'IN_PROGRESS' %}selected{% endif %}>In Progress</option>
                                <option value="COMPLETED" {% if ticket.status == 'COMPLETED' %}selected{% endif %}>Completed</option>
                            </select>
                         </form>
                    </td>
                    <td style="padding: 1rem; font-size: 0.9rem; color: var(--text-secondary);">{{ ticket.created_at|date:"M d H:i" }}</td>
                </tr>
                {% empty %}
                <tr>
                    <td colspan="6" style="padding: 2rem; text-align: center; color: var(--text-secondary);">No tickets found.</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>
{% endblock %}
"""

with open('tickets/templates/tickets/admin_panel_fixed.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("File created successfully with confirmed spaces.")
