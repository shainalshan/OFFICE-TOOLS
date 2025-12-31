import os

path = r"c:\Users\Shalu\.gemini\antigravity\scratch\office_tools_portal\backup_restore\templates\backup_restore\dashboard.html"

content = r"""{% extends 'core/base.html' %}

{% block title %}Backup & Restore | Office Portal{% endblock %}

{% block content %}
<div class="glass-container" style="max-width: 1000px; margin: 2rem auto; padding: 2rem;">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem;">
        <h1 style="color: #e2e8f0; font-size: 1.8rem;">Backup & Restore System</h1>
        <a href="{% url 'admin_dashboard' %}" style="color: #94a3b8; text-decoration: none;">&larr; Back to Admin</a>
    </div>

    <!-- Actions & Config Grid -->
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; margin-bottom: 2rem;">
        
        <!-- Backup Actions -->
        <div class="glass-container" style="background: rgba(255,255,255,0.03); padding: 1.5rem;">
            <h3 style="color: #667eea; margin-top: 0;">Manual Backup</h3>
            <p style="color: #94a3b8; font-size: 0.9rem; margin-bottom: 1.5rem;">
                Create a full backup of the system immediately. This includes the database and all files.
            </p>
            <form action="{% url 'trigger_backup' %}" method="post">
                {% csrf_token %}
                <button type="submit" style="background: #10b981; color: white; border: none; padding: 0.8rem 1.5rem; border-radius: 8px; cursor: pointer; font-weight: 600; width: 100%; transition: opacity 0.2s;">
                    START FULL BACKUP
                </button>
            </form>
        </div>

        <!-- Automated Config -->
        <div class="glass-container" style="background: rgba(255,255,255,0.03); padding: 1.5rem;">
            <h3 style="color: #f59e0b; margin-top: 0;">Automated Settings</h3>
            <form action="{% url 'configure_backup' %}" method="post">
                {% csrf_token %}
                <div style="margin-bottom: 1rem;">
                    <label style="display: flex; align-items: center; cursor: pointer; gap: 0.5rem; color: #e2e8f0;">
                        <input type="checkbox" name="auto_backup" {% if config.auto_backup %}checked{% endif %} id="auto_check">
                        Enable Automated Backups
                    </label>
                </div>

                <div style="margin-bottom: 1rem;">
                    <label style="color: #94a3b8; display: block; margin-bottom: 0.5rem; font-size: 0.9rem;">Frequency</label>
                    <select name="frequency" id="freq_select" style="width: 100%; padding: 0.5rem; background: rgba(0,0,0,0.3); border: 1px solid rgba(255,255,255,0.1); color: white; border-radius: 6px;">
                        <option value="daily" {% if config.frequency == 'daily' %}selected{% endif %}>Daily</option>
                        <option value="weekly" {% if config.frequency == 'weekly' %}selected{% endif %}>Weekly</option>
                        <option value="custom" {% if config.frequency == 'custom' %}selected{% endif %}>Custom Days</option>
                    </select>
                </div>

                <div id="custom_days_div" style="margin-bottom: 1rem; display: {% if config.frequency == 'custom' %}block{% else %}none{% endif %};">
                    <label style="color: #94a3b8; display: block; margin-bottom: 0.5rem; font-size: 0.9rem;">Every N Days</label>
                    <input type="number" name="custom_days" value="{{ config.custom_days }}" min="1" style="width: 100%; padding: 0.5rem; background: rgba(0,0,0,0.3); border: 1px solid rgba(255,255,255,0.1); color: white; border-radius: 6px;">
                </div>

                <button type="submit" style="background: #3b82f6; color: white; border: none; padding: 0.6rem 1.2rem; border-radius: 6px; cursor: pointer; width: 100%;">
                    Save Settings
                </button>
            </form>
        </div>
    </div>

    <!-- Restore Section -->
    <div class="glass-container" style="background: rgba(239, 68, 68, 0.05); padding: 1.5rem; margin-bottom: 2rem; border: 1px solid rgba(239, 68, 68, 0.2);">
        <h3 style="color: #ef4444; margin-top: 0;">⚠ System Restore</h3>
        <p style="color: #94a3b8; font-size: 0.9rem; margin-bottom: 1.5rem;">
            Restoring will <strong>OVERWRITE</strong> all current data and files. The server will restart automatically. 
            <strong>Super Admin authentication required.</strong>
        </p>
        
        <form action="{% url 'restore_backup' %}" method="post" enctype="multipart/form-data" style="display: flex; gap: 1rem; align-items: flex-end;">
            {% csrf_token %}
            <div style="flex: 1;">
                <label style="color: #94a3b8; display: block; margin-bottom: 0.5rem; font-size: 0.9rem;">Backup File (.zip)</label>
                <input type="file" name="backup_file" required accept=".zip" style="color: white;">
            </div>
            <div style="flex: 1;">
                <label style="color: #94a3b8; display: block; margin-bottom: 0.5rem; font-size: 0.9rem;">Admin Password</label>
                <input type="password" name="password" required placeholder="Enter password to confirm" style="width: 100%; padding: 0.5rem; background: rgba(0,0,0,0.3); border: 1px solid rgba(255,255,255,0.1); color: white; border-radius: 6px;">
            </div>
            <button type="submit" style="background: #ef4444; color: white; border: none; padding: 0.6rem 1.5rem; border-radius: 6px; cursor: pointer;" onclick="return confirm('ARE YOU SURE? This will restart the server and revert all data.');">
                RESTORE SYSTEM
            </button>
        </form>
    </div>

    <!-- Backup Logs -->
    <div class="glass-container" style="background: rgba(255,255,255,0.03); padding: 1.5rem;">
        <h3 style="color: #cbd5e1; margin-top: 0;">Recent Backup Logs</h3>
        <table style="width: 100%; border-collapse: collapse; margin-top: 1rem; color: #cbd5e1;">
            <thead>
                <tr style="border-bottom: 1px solid rgba(255,255,255,0.1); text-align: left;">
                    <th style="padding: 0.8rem;">Date</th>
                    <th style="padding: 0.8rem;">Filename</th>
                    <th style="padding: 0.8rem;">Size</th>
                    <th style="padding: 0.8rem;">Status</th>
                    <th style="padding: 0.8rem;">Action</th>
                </tr>
            </thead>
            <tbody>
                {% for log in logs %}
                <tr style="border-bottom: 1px solid rgba(255,255,255,0.05);">
                    <td style="padding: 0.8rem;">{{ log.created_at|date:"Y-m-d H:i" }}</td>
                    <td style="padding: 0.8rem;">{{ log.filename }}</td>
                    <td style="padding: 0.8rem;">{{ log.file_size|default:"-" }}</td>
                    <td style="padding: 0.8rem;">
                        {% if log.status == 'success' %}
                        <span style="color: #34d399;">Success</span>
                        {% elif log.status == 'failed' %}
                        <span style="color: #f87171;" title="{{ log.error_message }}">Failed ⓘ</span>
                        {% else %}
                        <span style="color: #fbbf24;">Running...</span>
                        {% endif %}
                    </td>
                    <td style="padding: 0.8rem;">
                        {% if log.status == 'success' %}
                        <a href="{% url 'download_backup' log.id %}" style="color: #60a5fa; text-decoration: none;">Download</a>
                        {% endif %}
                    </td>
                </tr>
                {% empty %}
                <tr>
                    <td colspan="5" style="padding: 1rem; text-align: center; color: #64748b;">No backups found.</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>

</div>

<script>
    const freqSelect = document.getElementById('freq_select');
    const customDiv = document.getElementById('custom_days_div');
    
    freqSelect.addEventListener('change', function() {
        if (this.value === 'custom') {
            customDiv.style.display = 'block';
        } else {
            customDiv.style.display = 'none';
        }
    });
</script>
{% endblock %}
"""

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print("File written successfully.")

# Verify
with open(path, 'r', encoding='utf-8') as f:
    read_content = f.read()
    if "{% if config.frequency == 'daily' %}" in read_content:
        print("VERIFICATION SUCCESS: Spaces found.")
    else:
        print("VERIFICATION FAILED: Spaces NOT found.")
