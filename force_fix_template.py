import os

content = """{% extends 'core/base.html' %}

{% block content %}
<div style='max-width: 1000px; margin: 0 auto; padding-bottom: 4rem;'>
    <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem;'>
        <div>
            <h1 style='margin: 0; font-size: 1.8rem;'>
                {% if is_admin_view %}
                📄 Timesheet: {{ timesheet.employee.first_name }}
                {% else %}
                📅 My Timesheet
                {% endif %}
            </h1>
            <p style='color: var(--text-secondary); margin-top: 0.5rem;'>{{ timesheet.period_start|date:'F Y' }}</p>
        </div>
        <div style='display: flex; gap: 1rem; align-items: center;'>
            {% if not is_admin_view %}
            <form method="get" style="margin: 0;">
                <input type="month" name="month" value="{{ timesheet.period_start|date:'Y-m' }}"
                    onchange="this.form.submit()"
                    style="padding: 0.5rem; border-radius: 8px; border: 1px solid rgba(255,255,255,0.1); background: rgba(0,0,0,0.2); color: white; font-family: inherit; cursor: pointer;">
            </form>
            {% endif %}

            <div class='glass-container' style='padding: 0.5rem 1rem; text-align: center;'>
                <div style='font-size: 0.8rem; color: var(--text-secondary);'>Total Hours</div>
                <div style='font-size: 1.2rem; font-weight: bold; color: #818cf8;'>{{ total_period_hours|default:'0.00' }}</div>
            </div>
            {% if not is_admin_view %}
            <a href="{% url 'hr_staff_portal' %}" class='btn-secondary'>Back to Punch</a>
            {% else %}
            <button onclick="window.close()" class="btn-secondary">
                Close View
            </button>
            {% endif %}
        </div>
    </div>
    <div class='glass-container' style='padding: 0;'>
        <table style='width: 100%; border-collapse: collapse;'>
            <thead>
                <tr style='background: rgba(255,255,255,0.05); text-align: left;'>
                    <th style='padding: 1rem;'>Date</th>
                    <th style='padding: 1rem;'>Status</th>
                    <th style='padding: 1rem;'>In</th>
                    <th style='padding: 1rem;'>Out</th>
                    <th style='padding: 1rem;'>Hours</th>
                    <th style='padding: 1rem;'>Notes</th>
                    <th style='padding: 1rem; text-align: right;'>Action</th>
                </tr>
            </thead>
            <tbody>
                {% for entry in entries %}
                <tr style='border-bottom: 1px solid rgba(255,255,255,0.05); {% if entry.date.weekday >= 5 %}background: rgba(0,0,0,0.2);{% endif %}'>
                    <td style='padding: 1rem;'>
                        <span style='font-weight: bold;'>{{ entry.date|date:'d' }}</span>
                        <span style='color: var(--text-secondary); font-size: 0.9rem;'>{{ entry.date|date:'D' }}</span>
                    </td>
                    <td style='padding: 1rem;'>
                        {% if entry.status == 'PRESENT' %}
                        <span style='color: #4ade80;'>Present</span>
                        {% elif entry.status == 'WEEK_OFF' %}
                        <span style='color: var(--text-secondary);'>Week Off</span>
                        {% elif entry.status == 'ABSENT' %}
                        <span style='color: #f87171;'>Absent</span>
                        {% else %}
                        <span style='color: #fbbf24;'>{{ entry.get_status_display }}</span>
                        {% endif %}

                        {% if entry.is_manual_adjustment %}
                        <span title="Manually Edited" style="cursor: help;">📝</span>
                        {% endif %}
                    </td>
                    <td style='padding: 1rem; color: #cbd5e1;'>{{ entry.first_punch_in|default:'--' }}</td>
                    <td style='padding: 1rem; color: #cbd5e1;'>{{ entry.last_punch_out|default:'--' }}</td>
                    <td style='padding: 1rem; font-weight: bold;'>{% if entry.total_hours > 0 %}{{ entry.total_hours }}h{% else %}--{% endif %}</td>
                    <td style='padding: 1rem; font-size: 0.9rem; color: var(--text-secondary);'>{{ entry.notes|default:'' }}</td>
                    <td style='padding: 1rem; text-align: right;'>
                        <button
                            onclick="openEditModal('{{ entry.id }}', '{{ entry.status }}', '{{ entry.date|date:'M d' }}', '{{ entry.first_punch_in|time:'H:i'|default:'' }}', '{{ entry.last_punch_out|time:'H:i'|default:'' }}')"
                            style="background: none; border: none; cursor: pointer; color: var(--text-secondary); font-size: 1.1rem; opacity: 0.7; transition: 0.2s;">
                            ✏️
                        </button>
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>

    <!-- Actions -->
    <div style='margin-top: 2rem; text-align: right;'>
        {% if timesheet.status == 'PENDING' or timesheet.status == 'REJECTED' %}
        
            {% if timesheet.status == 'REJECTED' %}
            <div style="background: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.3); padding: 1rem; border-radius: 8px; margin-bottom: 1rem; text-align: left;">
                <strong style="color: #ef4444;">❌ Timesheet Rejected</strong>
                <p style="margin: 0.5rem 0 0 0; color: #fca5a5;">Reason: {{ timesheet.rejection_reason|default:"No reason provided." }}</p>
            </div>
            {% endif %}

            <form method="post" action="{% url 'hr_submit_timesheet' %}">
                {% csrf_token %}
                <button type="submit" class="btn-primary">
                    {% if timesheet.status == 'REJECTED' %}Resubmit{% else %}Submit{% endif %} for Approval
                </button>
            </form>
            
        {% else %}
            <div style='background: rgba(16, 185, 129, 0.1); display: inline-block; padding: 1rem; border-radius: 8px; color: #4ade80; border: 1px solid rgba(16, 185, 129, 0.3);'>
                Status: <b>{{ timesheet.get_status_display }}</b>
            </div>
        {% endif %}
    </div>
</div>

<!-- Edit Modal -->
<div id="editModal"
    style="display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.6); backdrop-filter: blur(8px); z-index: 1000; justify-content: center; align-items: center; animation: fadeIn 0.2s ease-out;">
    <div
        style="width: 100%; max-width: 420px; background: #1e1b2e; border: 1px solid rgba(255,255,255,0.1); border-radius: 16px; padding: 2rem; box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5); transform: translateY(0); animation: slideUp 0.3s ease-out;">

        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem;">
            <h2
                style="margin: 0; font-size: 1.5rem; font-weight: 600; background: linear-gradient(135deg, #fff, #94a3b8); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                Edit Entry
            </h2>
            <span id="modalDate"
                style="font-size: 0.9rem; color: var(--text-secondary); background: rgba(255,255,255,0.05); padding: 0.25rem 0.75rem; border-radius: 20px;"></span>
        </div>

        <form id="editForm" onsubmit="submitEdit(event)">
            {% csrf_token %}
            <input type="hidden" id="editEntryId" name="entry_id">

            <div style="margin-bottom: 1.5rem;">
                <label
                    style="display: block; font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 0.5rem; margin-left: 0.2rem;">Status</label>
                <div style="position: relative;">
                    <select id="editStatus" name="status"
                        style="width: 100%; padding: 0.8rem 1rem; background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.1); border-radius: 10px; color: white; appearance: none; cursor: pointer; font-size: 0.95rem; transition: all 0.2s;">
                        <option value="PRESENT" style="background: #1e1b2e; color: white;">Present</option>
                        <option value="ABSENT" style="background: #1e1b2e; color: white;">Absent</option>
                        <option value="WEEK_OFF" style="background: #1e1b2e; color: white;">Week Off</option>
                        <option value="HOLIDAY" style="background: #1e1b2e; color: white;">Holiday</option>
                        <option value="SICK_LEAVE" style="background: #1e1b2e; color: white;">Sick Leave</option>
                        <option value="ANNUAL_LEAVE" style="background: #1e1b2e; color: white;">Annual Leave</option>
                        <option value="WFH" style="background: #1e1b2e; color: white;">Work From Home</option>
                    </select>
                    <div
                        style="position: absolute; right: 1rem; top: 50%; transform: translateY(-50%); pointer-events: none; color: var(--text-secondary);">
                        ▼
                    </div>
                </div>
            </div>

            <div style="margin-bottom: 2rem; display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                <div>
                    <label
                        style="display: block; font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 0.5rem; margin-left: 0.2rem;">In
                        Time</label>
                    <input type="time" name="first_in" id="editFirstIn"
                        style="width: 100%; padding: 0.8rem; background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.1); border-radius: 10px; color: white; font-family: monospace; font-size: 1rem; transition: all 0.2s;">
                </div>
                <div>
                    <label
                        style="display: block; font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 0.5rem; margin-left: 0.2rem;">Out
                        Time</label>
                    <input type="time" name="last_out" id="editLastOut"
                        style="width: 100%; padding: 0.8rem; background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.1); border-radius: 10px; color: white; font-family: monospace; font-size: 1rem; transition: all 0.2s;">
                </div>
            </div>

            <div style="display: flex; gap: 1rem;">
                <button type="button" onclick="closeEditModal()"
                    style="flex: 1; padding: 0.8rem; border-radius: 10px; border: 1px solid rgba(255,255,255,0.1); background: transparent; color: var(--text-secondary); cursor: pointer; font-weight: 500; transition: all 0.2s;">
                    Cancel
                </button>
                <button type="submit"
                    style="flex: 2; padding: 0.8rem; border-radius: 10px; border: none; background: #6366f1; color: white; cursor: pointer; font-weight: 600; box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3); transition: all 0.2s;">
                    Save Changes
                </button>
            </div>
        </form>
    </div>
</div>

<style>
    @keyframes fadeIn {
        from {
            opacity: 0;
        }

        to {
            opacity: 1;
        }
    }

    @keyframes slideUp {
        from {
            transform: translateY(20px);
            opacity: 0;
        }

        to {
            transform: translateY(0);
            opacity: 1;
        }
    }

    #editStatus:focus,
    input[type="time"]:focus {
        outline: none;
        border-color: #6366f1 !important;
        background: rgba(99, 102, 241, 0.1) !important;
    }

    button:hover {
        transform: translateY(-1px);
    }

    button[type="submit"]:hover {
        background: #4f46e5 !important;
        box-shadow: 0 6px 16px rgba(99, 102, 241, 0.4) !important;
    }

    /* Ensure drop down options are dark */
    select option {
        background: #1e1b2e;
        color: white;
    }

    /* Custom Time Picker icon brightness for dark mode */
    input[type="time"]::-webkit-calendar-picker-indicator {
        filter: invert(1);
        cursor: pointer;
        opacity: 0.6;
    }

    input[type="time"]::-webkit-calendar-picker-indicator:hover {
        opacity: 1;
    }
</style>

<script>
    function openEditModal(id, currentStatus, dateStr, firstIn, lastOut) {
        document.getElementById('editEntryId').value = id;
        document.getElementById('editStatus').value = currentStatus;
        document.getElementById('modalDate').innerText = `(${dateStr})`;

        document.getElementById('editFirstIn').value = firstIn || '';
        document.getElementById('editLastOut').value = lastOut || '';

        document.getElementById('editModal').style.display = 'flex';
    }

    function closeEditModal() {
        document.getElementById('editModal').style.display = 'none';
    }

    function submitEdit(event) {
        if (event) event.preventDefault();

        const formData = new FormData(document.getElementById('editForm'));

        // Manual FETCH to debug
        fetch("{% url 'hr_update_entry' %}", {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    location.reload();
                } else {
                    alert('Error: ' + data.message);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred.');
            });
    }

    // Close on click outside
    document.getElementById('editModal').addEventListener('click', function (e) {
        if (e.target === this) closeEditModal();
    });
</script>
{% endblock %}
"""

with open(r'c:\Users\Shalu\.gemini\antigravity\scratch\office_tools_portal\hr\templates\hr\timesheet_view.html', 'w', encoding='utf-8') as f:
    f.write(content)
print("SUCCESS: File overwritten.")
