import os

file_path = r'c:\Users\Shalu\.gemini\antigravity\scratch\office_tools_portal\backup_restore\templates\backup_restore\dashboard_v7.html'

# The corrected content with CLEANED UP tags (no newlines inside tags)
content = r"""{% extends 'core/base.html' %}
{% load static %}

{% block title %}Backup & Restore Dashboard{% endblock %}

{% block content %}
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    :root {
        --bg-dark: #0f172a;
        --card-bg: rgba(30, 41, 59, 0.4);
        --glass-border: rgba(255, 255, 255, 0.08);
        --primary-gradient: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        --success-gradient: linear-gradient(135deg, #10b981 0%, #059669 100%);
        --danger-gradient: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        --text-primary: #f8fafc;
        --text-secondary: #94a3b8;
        --input-bg: rgba(15, 23, 42, 0.6);
        --accent-purple: #8b5cf6;
        --accent-blue: #3b82f6;
    }

    body {
        background-color: #0f0c29;
        background-image:
            radial-gradient(at 0% 0%, rgba(76, 29, 149, 0.3) 0px, transparent 50%),
            radial-gradient(at 100% 0%, rgba(59, 130, 246, 0.3) 0px, transparent 50%),
            radial-gradient(at 100% 100%, rgba(15, 23, 42, 1) 0px, transparent 50%),
            radial-gradient(at 0% 100%, rgba(30, 41, 59, 1) 0px, transparent 50%);
        background-attachment: fixed;
        color: var(--text-primary);
        font-family: 'Inter', sans-serif;
        min-height: 100vh;
    }

    .dashboard-container {
        max-width: 1200px;
        margin: 2rem auto;
        padding: 0 1.5rem;
    }

    /* Glassmorphism Utilities */
    .glass-panel {
        background: var(--card-bg);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid var(--glass-border);
        border-radius: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
    }

    /* Header */
    .header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 2rem;
        padding: 1.25rem 2rem;
    }

    .logo-area {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        font-size: 1.5rem;
        font-weight: 700;
        letter-spacing: -0.025em;
    }

    .logo-icon {
        color: var(--accent-purple);
    }

    .logo-text {
        background: linear-gradient(to right, #8b5cf6, #3b82f6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .user-controls {
        display: flex;
        align-items: center;
        gap: 1.5rem;
        font-size: 0.9rem;
    }

    .nav-link {
        color: var(--text-secondary);
        text-decoration: none;
        transition: color 0.2s;
    }

    .nav-link:hover {
        color: var(--text-primary);
    }

    .logout-link {
        color: #fca5a5;
    }

    .logout-link:hover {
        color: #ef4444;
    }

    /* Grid Layout */
    .grid-split {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 2rem;
        margin-bottom: 2rem;
    }

    .card {
        padding: 2rem;
        display: flex;
        flex-direction: column;
        height: 100%;
    }

    .card-title {
        font-size: 1.25rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
        color: white;
    }

    .card-subtitle {
        color: var(--text-secondary);
        font-size: 0.875rem;
        margin-bottom: 2rem;
    }

    /* Controls */
    .radio-group {
        display: flex;
        background: rgba(15, 23, 42, 0.5);
        padding: 0.25rem;
        border-radius: 12px;
        border: 1px solid var(--glass-border);
        margin-bottom: 2rem;
    }

    .radio-option {
        flex: 1;
        position: relative;
    }

    .radio-option input {
        position: absolute;
        opacity: 0;
        cursor: pointer;
        height: 100%;
        width: 100%;
        z-index: 10;
    }

    .radio-label-content {
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 0.75rem;
        border-radius: 10px;
        color: var(--text-secondary);
        font-weight: 500;
        transition: all 0.3s;
        gap: 0.5rem;
    }

    .radio-option input:checked+.radio-label-content {
        background: var(--accent-blue);
        /* Fallback */
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.3) 0%, rgba(37, 99, 235, 0.3) 100%);
        color: white;
        box-shadow: 0 0 15px rgba(59, 130, 246, 0.3);
        border: 1px solid rgba(59, 130, 246, 0.5);
    }

    /* Progress Bar */
    .progress-container {
        margin-bottom: 2rem;
    }

    .progress-bar-bg {
        height: 8px;
        background: rgba(255, 255, 255, 0.05);
        border-radius: 4px;
        overflow: hidden;
    }

    .progress-bar-fill {
        height: 100%;
        width: 0%;
        background: var(--primary-gradient);
        box-shadow: 0 0 10px rgba(139, 92, 246, 0.5);
        transition: width 0.4s ease;
    }

    /* Buttons */
    .btn {
        width: 100%;
        padding: 1rem;
        border: none;
        border-radius: 12px;
        font-weight: 600;
        color: white;
        cursor: pointer;
        transition: transform 0.2s, opacity 0.2s;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-size: 0.9rem;
    }

    .btn:hover {
        transform: translateY(-2px);
        opacity: 0.9;
    }

    .btn-success {
        background: var(--success-gradient);
        box-shadow: 0 4px 15px rgba(16, 185, 129, 0.4);
    }

    .btn-danger {
        background: var(--danger-gradient);
        box-shadow: 0 4px 15px rgba(239, 68, 68, 0.4);
    }

    .btn-secondary {
        background: rgba(255, 255, 255, 0.1);
        width: auto;
        padding: 0.75rem 1.5rem;
        text-transform: none;
    }

    /* Form Inputs */
    .form-group {
        margin-bottom: 1.5rem;
    }

    .input-label {
        display: block;
        color: var(--text-secondary);
        margin-bottom: 0.5rem;
        font-size: 0.875rem;
    }

    .form-control,
    .form-select {
        width: 100%;
        background: var(--input-bg);
        border: 1px solid var(--glass-border);
        padding: 0.75rem 1rem;
        border-radius: 10px;
        color: white;
        font-family: inherit;
        outline: none;
        transition: border-color 0.2s, box-shadow 0.2s;
    }

    .form-control:focus,
    .form-select:focus {
        border-color: var(--accent-purple);
        box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.2);
    }

    /* Range Slider */
    input[type=range] {
        -webkit-appearance: none;
        width: 100%;
        background: transparent;
    }

    input[type=range]::-webkit-slider-thumb {
        -webkit-appearance: none;
        height: 20px;
        width: 20px;
        border-radius: 50%;
        background: white;
        cursor: pointer;
        margin-top: -8px;
        box-shadow: 0 0 10px rgba(255, 255, 255, 0.5);
    }

    input[type=range]::-webkit-slider-runnable-track {
        width: 100%;
        height: 4px;
        cursor: pointer;
        background: rgba(255, 255, 255, 0.2);
        border-radius: 2px;
    }

    /* Toggle Switch */
    .switch {
        position: relative;
        display: inline-block;
        width: 48px;
        height: 26px;
    }

    .switch input {
        opacity: 0;
        width: 0;
        height: 0;
    }

    .slider {
        position: absolute;
        cursor: pointer;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background-color: rgba(15, 23, 42, 0.8);
        transition: .4s;
        border-radius: 34px;
        border: 1px solid var(--glass-border);
    }

    .slider:before {
        position: absolute;
        content: "";
        height: 18px;
        width: 18px;
        left: 3px;
        bottom: 3px;
        background-color: white;
        transition: .4s;
        border-radius: 50%;
    }

    input:checked+.slider {
        background-color: var(--accent-purple);
    }

    input:checked+.slider:before {
        transform: translateX(22px);
    }

    /* Danger Zone */
    .danger-zone {
        border: 1px solid rgba(239, 68, 68, 0.3);
        background: linear-gradient(to right, rgba(239, 68, 68, 0.05), transparent);
    }

    .danger-header {
        color: #fca5a5;
        font-weight: 600;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    /* Table */
    .table-responsive {
        overflow-x: auto;
    }

    .logs-table {
        width: 100%;
        border-collapse: collapse;
        color: var(--text-secondary);
    }

    .logs-table th {
        text-align: left;
        padding: 1rem;
        border-bottom: 1px solid var(--glass-border);
        font-weight: 500;
        color: white;
    }

    .logs-table td {
        padding: 1rem;
        border-bottom: 1px solid var(--glass-border);
    }

    .logs-no-data {
        text-align: center;
        padding: 2rem;
        color: var(--text-secondary);
    }

    .badge {
        padding: 0.25rem 0.75rem;
        border-radius: 99px;
        font-size: 0.75rem;
        font-weight: 600;
    }

    .badge-full {
        background: rgba(139, 92, 246, 0.2);
        color: #c4b5fd;
    }

    .badge-file {
        background: rgba(16, 185, 129, 0.2);
        color: #6ee7b7;
    }

    .action-btn {
        background: transparent;
        border: none;
        color: var(--text-secondary);
        cursor: pointer;
        font-size: 1.1rem;
        margin-right: 0.5rem;
        transition: color 0.2s;
    }

    .action-btn:hover {
        color: white;
    }

    /* Input Group */
    .input-group {
        display: flex;
        gap: 0.5rem;
    }

    .input-group .form-control {
        border-radius: 10px 0 0 10px;
    }

    .input-group .btn-secondary {
        border-radius: 0 10px 10px 0;
        width: auto;
    }
</style>

<div class="dashboard-container">
    {% if messages %}
    <div style="margin-bottom: 2rem;">
        {% for message in messages %}
        <div class="glass-panel"
            style="padding: 1rem; border-left: 4px solid {% if message.tags == 'success' %}#10b981{% else %}#ef4444{% endif %}; color: white;">
            {{ message }}
        </div>
        {% endfor %}
    </div>
    {% endif %}

    <!-- Header -->
    <header class="header glass-panel">
        <div class="logo-area">
            <span class="logo-icon">✨</span>
            <span class="logo-text">Office Portal</span>
        </div>
        <div class="user-controls">
            <span>Welcome, {{ request.user.username }}</span>
            <a href="/admin/" class="nav-link">Admin Panel</a>
            <span style="color: var(--glass-border);">|</span>
            <a href="{% url 'logout' %}" class="nav-link logout-link">Logout</a>
        </div>
    </header>

    <!-- Top Section: Split Layout -->
    <div class="grid-split">
        <!-- Manual Backup Card -->
        <div class="glass-panel card">
            <h2 class="card-title">Manual Backup</h2>
            <p class="card-subtitle">Create a full backup of the system immediately. This includes the database and all
                files.</p>

            <form action="{% url 'trigger_backup' %}" method="POST" id="manualBackupForm"
                style="flex-grow: 1; display: flex; flex-direction: column;">
                {% csrf_token %}

                <div class="radio-group">
                    <label class="radio-option">
                        <input type="radio" name="backup_type" value="full" checked onclick="updateBackupBtn('full')">
                        <div class="radio-label-content">
                            <span>⚫</span> Full Backup
                        </div>
                    </label>
                    <label class="radio-option">
                        <input type="radio" name="backup_type" value="file" onclick="updateBackupBtn('file')">
                        <div class="radio-label-content">
                            <span>📁</span> File Only
                        </div>
                    </label>
                </div>

                <div class="progress-container">
                    <div
                        style="display: flex; justify-content: space-between; margin-bottom: 0.5rem; font-size: 0.8rem; color: var(--text-secondary);">
                        <span>Status</span>
                        <span id="progressText">Ready</span>
                    </div>
                    <div class="progress-bar-bg">
                        <div class="progress-bar-fill" id="progressBar"></div>
                    </div>
                </div>

                <div style="margin-top: auto;">
                    <button type="submit" class="btn btn-success" id="startBackupBtn">Start Full Backup</button>
                </div>
            </form>
        </div>

        <!-- Automated Settings Card -->
        <div class="glass-panel card">
            <div style="display: flex; justify-content: space-between; align-items: start;">
                <div>
                    <h2 class="card-title" style="color: #fbbf24;">Automated Settings</h2>
                    <p class="card-subtitle">Configure schedule and retention.</p>
                </div>
                <!-- Enable Switch -->
                <label class="switch">
                    <input type="checkbox" form="settingsForm" name="auto_backup" {% if config.auto_backup %}checked{% endif %}>
                    <span class="slider"></span>
                </label>
            </div>

            <form action="{% url 'configure_backup' %}" method="POST" id="settingsForm">
                {% csrf_token %}

                <div class="form-group">
                    <label class="input-label">Frequency</label>
                    <select name="frequency" class="form-select">
                        <option value="hourly" {% if config.frequency == 'hourly' %}selected{% endif %}>Hourly</option>
                        <option value="daily" {% if config.frequency == 'daily' %}selected{% endif %}>Daily</option>
                        <option value="weekly" {% if config.frequency == 'weekly' %}selected{% endif %}>Weekly</option>
                    </select>
                </div>

                <div class="form-group">
                    <label class="input-label" style="display: flex; justify-content: space-between;">
                        <span>Retention Policy</span>
                        <span style="color: white; font-weight: 600;"><span id="retentionVal">{{ config.retention_days }}</span> Days</span>
                    </label>
                    <input type="range" name="retention_days" min="1" max="90" value="{{ config.retention_days }}"
                        oninput="document.getElementById('retentionVal').innerText = this.value">
                </div>

                <div class="form-group">
                    <label class="input-label">Email Notifications</label>
                    <div style="display: flex; gap: 1.5rem;">
                        <label
                            style="display: flex; gap: 0.5rem; color: var(--text-secondary); align-items: center; cursor: pointer;">
                            <input type="checkbox" name="email_notifications" {% if config.email_notifications %}checked{% endif %}> Enable
                        </label>
                        <label
                            style="display: flex; gap: 0.5rem; color: var(--text-secondary); align-items: center; cursor: pointer;">
                            <input type="checkbox" name="email_files_only" {% if config.email_files_only %}checked{% endif %}> Files Only
                        </label>
                    </div>
                </div>

                <div class="form-group">
                    <label class="input-label">Local Server Storage Path</label>
                    <div class="input-group">
                        <input type="text" name="backup_path" id="backupPath" value="{{ config.backup_path }}"
                            class="form-control" placeholder="/var/www/backups/">
                        <button type="button" class="btn btn-secondary" onclick="browsePath()">Browse</button>
                    </div>
                </div>

                <button type="submit" class="btn"
                    style="background: rgba(255,255,255,0.05); border: 1px solid var(--glass-border); margin-top: 1rem;">
                    Save Configuration
                </button>
            </form>
        </div>
    </div>

    <!-- System Restore -->
    <div class="glass-panel danger-zone" style="padding: 2rem; margin-bottom: 2rem;">
        <div class="danger-header">
            <span style="font-size: 1.25rem;">⚠️</span>
            <span>System Restore</span>
        </div>
        <p style="color: #fca5a5; margin-bottom: 2rem; opacity: 0.8; font-size: 0.9rem;">
            Restoring will <strong style="text-decoration: underline;">OVERWRITE</strong> all current data and files.
            The server will restart automatically upon completion.
        </p>

        <form action="{% url 'restore_backup' %}" method="POST" enctype="multipart/form-data">
            {% csrf_token %}
            <div style="display: grid; grid-template-columns: 2fr 1fr auto; gap: 1.5rem; align-items: end;">
                <div class="form-group" style="margin: 0;">
                    <label class="input-label">Backup File (.zip)</label>
                    <input type="file" name="backup_file" class="form-control" accept=".zip" style="padding: 0.5rem;">
                </div>
                <div class="form-group" style="margin: 0;">
                    <label class="input-label">Admin Password</label>
                    <input type="password" name="password" class="form-control" placeholder="Required to confirm">
                </div>
                <button type="submit" class="btn btn-danger"
                    style="width: auto; padding-left: 2rem; padding-right: 2rem;"
                    onclick="return confirm('CRITICAL WARNING: This will overwrite your database and files. Are you absolutely sure?')">
                    Restore System
                </button>
            </div>
        </form>
    </div>

    <!-- Logs -->
    <div class="glass-panel" style="padding: 2rem; min-height: 300px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;">
            <h2 class="card-title" style="margin: 0;">Recent Backup Logs</h2>
            <div style="display: flex; gap: 1rem;">
                <!-- Search or Filters could go here -->
            </div>
        </div>

        <div class="table-responsive">
            <table class="logs-table">
                <thead>
                    <tr>
                        <th>Date</th>
                        <th>Filename</th>
                        <th>Type</th>
                        <th>Size</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {% for log in logs %}
                    <tr>
                        <td>{{ log.created_at|date:"Y-m-d H:i" }}</td>
                        <td>{{ log.filename }}</td>
                        <td>
                            {% if log.backup_type == 'full' %}
                            <span class="badge badge-full">FULL</span>
                            {% else %}
                            <span class="badge badge-file">FILE</span>
                            {% endif %}
                        </td>
                        <td>{{ log.file_size }}</td>
                        <td>
                            <a href="{% url 'download_backup' log.id %}" class="action-btn" title="Download">⬇️</a>
                            <a href="#" class="action-btn" title="View details">👁️</a>
                            <!-- Delete not wired up yet -->
                            <a href="#" class="action-btn" style="color: #ef4444;" title="Delete">🗑️</a>
                        </td>
                    </tr>
                    {% empty %}
                    <tr>
                        <td colspan="5" class="logs-no-data">No backup logs found.</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</div>

<script>
    function updateBackupBtn(type) {
        const btn = document.getElementById('startBackupBtn');
        if (type === 'full') {
            btn.innerText = 'Start Full Backup';
        } else {
            btn.innerText = 'Start File Backup';
        }
    }

    function browsePath() {
        // We will ping a backend endpoint that opens a local folder browser on the server
        // NOTE: This only works because the server is local to the user (desktop app context)
        const input = document.getElementById('backupPath');
        const originalText = input.value;
        input.placeholder = "Opening browser...";

        fetch("{% url 'browse_path' %}")
            .then(response => response.json())
            .then(data => {
                if (data.path) {
                    input.value = data.path;
                } else if (data.error) {
                    alert('Error: ' + data.error);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Could not open folder browser.');
            });
    }

    // Optional: Simulating progress for UX if backend doesn't push it
    const form = document.getElementById('manualBackupForm');
    form.addEventListener('submit', function () {
        const bar = document.getElementById('progressBar');
        const text = document.getElementById('progressText');
        text.innerText = "Processing...";
        bar.style.width = "30%";

        // Let the form submit naturally, page reload will show result
    });
</script>

{% endblock %}
"""

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("File overwritten successfully.")
