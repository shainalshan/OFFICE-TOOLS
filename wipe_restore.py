
import os

content = r"""{% extends 'core/base.html' %}
{% load waffle_tags %}

{% block content %}
<div class="animate-fade-in">
    <div style="margin-bottom: 2rem;">
        <a href="{% url 'my_tickets' %}"
            style="color: var(--text-secondary); text-decoration: none; display: inline-flex; align-items: center; gap: 0.5rem;">
            ← Back to Tickets
        </a>
    </div>

    <div style="display: grid; grid-template-columns: 2fr 1fr; gap: 2rem;">
        <!-- Left Column: Ticket Details & Comments -->
        <div>
            <!-- Ticket Header -->
            <div class="glass-container" style="padding: 2rem; margin-bottom: 2rem;">
                <div
                    style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1.5rem;">
                    <div>
                        <h1 style="margin: 0; font-size: 1.8rem;">{{ ticket.ticket_id }}</h1>
                        <p style="color: var(--text-secondary); margin: 0.5rem 0 0 0;">
                            Created by {{ ticket.user.username }} on {{ ticket.created_at|date:"M d, Y H:i" }}
                        </p>
                    </div>
                    <span class="badge badge-{{ ticket.status }}" style="font-size: 1rem; padding: 0.5rem 1rem;">
                        {{ ticket.get_status_display }}
                    </span>
                </div>

                <div
                    style="background: rgba(0,0,0,0.2); padding: 1.5rem; border-radius: 8px; border: 1px solid rgba(255,255,255,0.05);">
                    <h3 style="margin-top: 0; font-size: 1rem; color: var(--text-secondary); margin-bottom: 0.5rem;">
                        Issue Description</h3>
                    <p
                        style="line-height: 1.6; margin: 0; white-space: pre-wrap; word-wrap: break-word; overflow-wrap: break-word; word-break: break-word;">
                        {{ ticket.issue }}</p>

                    <!-- Ticket Attachments -->
                    {% flag "ticket_attachments" %}
                    <div style="margin-top: 1rem; display: flex; flex-wrap: wrap; gap: 0.5rem;">
                        {% for att in ticket.attachments.all %}
                        {% if not att.comment %}
                        <a href="{{ att.file.url }}" target="_blank"
                            style="display: inline-flex; align-items: center; gap: 0.3rem; background: rgba(255,255,255,0.1); padding: 0.3rem 0.6rem; border-radius: 4px; color: white; text-decoration: none; font-size: 0.85rem; border: 1px solid rgba(255,255,255,0.2);">
                            📎 {{ att.file.name|slice:"12:" }}
                        </a>
                        {% endif %}
                        {% endfor %}
                    </div>
                    {% endflag %}
                </div>

                {% if ticket.assigned_to %}
                <div
                    style="margin-top: 1rem; display: flex; align-items: center; gap: 0.5rem; color: var(--text-secondary); font-size: 0.9rem;">
                    <span>👤 Assigned to: <strong style="color: white;">{{ ticket.assigned_to.username }}</strong></span>
                </div>
                {% endif %}
            </div>

            <!-- Comments Section -->
            <div class="glass-container" style="padding: 2rem;">
                <h2 style="margin-top: 0; margin-bottom: 1.5rem;">Comments & Updates</h2>

                <div style="display: flex; flex-direction: column; gap: 1.5rem; margin-bottom: 2rem;">
                    {% for comment in comments %}
                    <div style="display: flex; gap: 1rem;">
                        <div
                            style="width: 40px; height: 40px; border-radius: 50%; background: linear-gradient(135deg, #667eea, #764ba2); display: flex; align-items: center; justify-content: center; font-weight: bold; flex-shrink: 0;">
                            {{ comment.user.username|make_list|first|upper }}
                        </div>
                        <div style="flex: 1;">
                            <div style="display: flex; justify-content: space-between; margin-bottom: 0.25rem;">
                                <span style="font-weight: 600;">{{ comment.user.username }}</span>
                                <span style="font-size: 0.8rem; color: var(--text-secondary);">{{ comment.created_at|timesince }} ago</span>
                            </div>
                            <div
                                style="background: rgba(255,255,255,0.05); padding: 1rem; border-radius: 0 12px 12px 12px; border: 1px solid rgba(255,255,255,0.1); word-wrap: break-word; overflow-wrap: break-word; word-break: break-word;">
                                {{ comment.text|linebreaksbr }}

                                <!-- Comment Attachments -->
                                {% flag "ticket_attachments" %}
                                {% if comment.attachments.exists %}
                                <div
                                    style="margin-top: 0.8rem; padding-top: 0.8rem; border-top: 1px solid rgba(255,255,255,0.1); display: flex; flex-wrap: wrap; gap: 0.5rem;">
                                    {% for att in comment.attachments.all %}
                                    <a href="{{ att.file.url }}" target="_blank"
                                        style="display: inline-flex; align-items: center; gap: 0.3rem; color: #60a5fa; text-decoration: none; font-size: 0.85rem;">
                                        📎 {{ att.file.name|slice:"12:" }}
                                    </a>
                                    {% endfor %}
                                </div>
                                {% endif %}
                                {% endflag %}
                            </div>
                        </div>
                    </div>
                    {% empty %}
                    <div style="text-align: center; color: var(--text-secondary); padding: 2rem;">
                        No comments yet.
                    </div>
                    {% endfor %}
                </div>

                <!-- Add Comment Form -->
                {% if ticket.status != 'COMPLETED' and ticket.status != 'CANCELLED' %}
                <form method="post" enctype="multipart/form-data"
                    style="border-top: 1px solid rgba(255,255,255,0.1); padding-top: 1.5rem;">
                    {% csrf_token %}
                    <input type="hidden" name="action" value="comment">
                    <textarea name="text" rows="3" placeholder="Type your comment here..." required
                        style="width: 100%; background: rgba(0,0,0,0.2); border: 1px solid rgba(255,255,255,0.2); border-radius: 8px; color: white; padding: 1rem; font-family: inherit; margin-bottom: 1rem; box-sizing: border-box;"></textarea>

                    {% flag "ticket_attachments" %}
                    <div style="margin-bottom: 1rem;">
                        <input type="file" name="attachment" class="form-control"
                            style="font-size: 0.9rem; color: var(--text-secondary);">
                    </div>
                    {% endflag %}

                    <div style="text-align: right;">
                        <button type="submit" class="btn-primary" style="width: auto;">Post Comment</button>
                    </div>
                </form>
                {% else %}
                <div
                    style="text-align: center; color: var(--text-secondary); background: rgba(0,0,0,0.2); padding: 1rem; border-radius: 8px;">
                    This ticket is closed. No further comments allowed.
                </div>
                {% endif %}
            </div>
        </div>

        <!-- Right Column: Actions -->
        <div>
            <div class="glass-container" style="padding: 1.5rem; position: sticky; top: 2rem;">
                <h3 style="margin-top: 0; margin-bottom: 1rem;">Actions</h3>

                <!-- Status Update (Assignee/Admin) -->
                {% if is_assignee or is_admin %}
                {% if ticket.status != 'COMPLETED' and ticket.status != 'CANCELLED' %}
                <form method="post" style="margin-bottom: 1.5rem;">
                    {% csrf_token %}
                    <input type="hidden" name="action" value="status">
                    <label
                        style="display: block; margin-bottom: 0.5rem; color: var(--text-secondary); font-size: 0.9rem;">Update
                        Status</label>
                    <select name="new_status"
                        style="width: 100%; padding: 0.5rem; background: rgba(0,0,0,0.2); border: 1px solid rgba(255,255,255,0.2); border-radius: 6px; color: white; margin-bottom: 0.8rem;">
                        <option value="PENDING" {% if ticket.status == 'PENDING' %}selected{% endif %}>Pending</option>
                        <option value="IN_PROGRESS" {% if ticket.status == 'IN_PROGRESS' %}selected{% endif %}>In Progress
                        </option>
                        <option value="COMPLETED" {% if ticket.status == 'COMPLETED' %}selected{% endif %}>Completed
                        </option>
                    </select>
                    <button type="submit" class="btn-primary" style="width: 100%; padding: 0.5rem;">Update
                        Status</button>
                </form>
                <hr style="border: 0; border-top: 1px solid rgba(255,255,255,0.1); margin: 1.5rem 0;">
                {% endif %}
                {% endif %}

                <!-- Cancel Ticket -->
                {% if ticket.status != 'COMPLETED' and ticket.status != 'CANCELLED' %}
                <form method="post" onsubmit="return confirm('Are you sure you want to cancel this ticket?');">
                    {% csrf_token %}
                    <input type="hidden" name="action" value="cancel">
                    <button type="submit"
                        style="width: 100%; padding: 0.75rem; background: rgba(239, 68, 68, 0.1); color: #ef4444; border: 1px solid rgba(239, 68, 68, 0.3); border-radius: 8px; cursor: pointer; font-weight: 600; transition: all 0.2s;">
                        Cancel Ticket
                    </button>
                </form>
                {% endif %}

                <!-- Info -->
                <div style="margin-top: 1.5rem; font-size: 0.85rem; color: var(--text-secondary);">
                    <p style="margin-bottom: 0.5rem;"><strong>Priority:</strong> <span
                            class="dot-{{ ticket.priority }}">{{ ticket.get_priority_display }}</span></p>
                    {% if ticket.resolution %}
                    <div
                        style="margin-top: 1rem; background: rgba(16, 185, 129, 0.1); padding: 0.8rem; border-radius: 6px; border: 1px solid rgba(16, 185, 129, 0.2);">
                        <strong style="color: #34d399; display: block; margin-bottom: 0.3rem;">Resolution:</strong>
                        {{ ticket.resolution }}
                    </div>
                    {% endif %}
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
"""

path = r"tickets\templates\tickets\ticket_detail.html"
with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("File forced overwrite complete.")
