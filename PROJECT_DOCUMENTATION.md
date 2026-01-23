# Office Tools Portal - Project Documentation

## 1. Project Overview
The **Office Tools Portal** is a centralized web application designed to manage various internal office operations including IT ticketing, HR timesheets, Asset tracking, and communication tools. It is built using **Django (Python)** and provides a role-based access control system.

---

## 2. Core System & Authentication
### Features
*   **Authentication**: Secure Login, Logout, and Registration.
    *   *Note*: New user registrations require **Admin Approval** before they can log in.
*   **User Roles**:
    *   **Superuser**: Full access to the Django Admin and all Portal tools.
    *   **Tool-Specific Roles**: Access is granted per-tool (e.g., 'Ticketing', 'HR', 'Assets') via the *User Tool Access* system.
*   **Web Dashboard**: The landing page (`/dashboard`) for Admins to manage users, approve registrations, and configure notification settings.
*   **Notifications**: Centralized system for alerts (Ticket updates, Timesheet submissions, etc.). accessible via the bell icon.

---

## 3. Modules & Features

### 3.1. IT Ticketing System (`/tickets/`)
A complete helpdesk solution for managing internal support requests.

*   **User Features**:
    *   **Create Ticket**: Submit issues with **Priority** (Critical, High, Medium, Low) and optional **Deadline**.
    *   **My Tickets**: View status of created tickets.
    *   **History**: View archive of Completed/Cancelled tickets.
*   **Admin/Support Features**:
    *   **Admin Panel (V6)**: Comprehensive dashboard to view, filter, and manage all tickets.
    *   **Assignment**: Assign tickets to specific support staff.
    *   **Workflow**:
        1.  **Pending**: Acknowledged.
        2.  **In Progress**: Being worked on.
        3.  **Completed**: Resolved (Auto-hidden after 24h).
        4.  **Cancelled**: Invalid or withdrawn.
    *   **Reports**: Analytics on ticket volume and status. Exportable to **Excel** & **PDF**.
*   **Logic**:
    *   Only users in **Ticket Admin** or **Ticket Support** groups can be assigned tickets.
    *   Status changes trigger email and system notifications.

### 3.2. HR & Staff Portal (`/hr/`)
Manages employee attendance and timesheets.

*   **Staff Portal**:
    *   **Punch In/Out**: Single-click interface for daily attendance.
    *   **Daily Log**: View today’s punch history.
*   **Timesheets**:
    *   **Auto-Generation**: System builds timesheets based on daily punches.
    *   **Manual Entry**: Users can request manual time adjustments (e.g., missed punch).
    *   **Submission**: End-of-month submission for approval.
*   **HR Admin**:
    *   **Dashboard**: View Pending Approvals and Approved Timesheets.
    *   **Approval Workflow**: Approve or Reject timesheets with comments.
    *   **Export**: Download specific timesheets as **Excel** files.

### 3.3. Asset Management (`/assets/`)
Tracks company hardware and devices.

*   **Dashboard**:
    *   **Location Tabs**: Filter assets by location (e.g., DUBAI, LONDON).
    *   **Stats**: Live counters for Mac, Windows, iPhones, and Replacements.
*   **Features**:
    *   **Staff List**: Syncs with Contacts to show possession counts per employee.
    *   **Manage Assets**: Add/Edit/Delete asset records.
    *   **Rules**:
        *   **Resigned**: Requires "Staff in Possession" to be set.
        *   **Replacement**: Allows duplicate Serial Numbers (for swap units).
    *   **Export**: Download asset inventory as **Excel**.

### 3.4. Tools & Utilities

#### Email Signature Generator (`/signature/`)
*   **Function**: Generates standardized HTML email signatures.
*   **Inputs**: Name, Designation, Contact details, Photo (Max 50KB).
*   **Output**: Renders a template (Pixl or Invespy style) and provides a **Download HTML** option.

#### Office News & Chat (`/news/`)
*   **Feed**: A chat-like interface for company announcements and updates.
*   **Live Sync**: Auto-refreshes for new messages.
*   **Types**: News, Alerts, General.

#### Contacts Directory (`/contacts/`)
*   **Directory**: Searchable list of external/internal contacts.
*   **VCF Download**: Download all contacts as a **ZIP** file (optimized for iOS/Mobile import).

#### Image Compressor (`/tools/compressor/`)
*   **Function**: Compresses high-res images to **under 50KB** (JPEG format).
*   **Usage**: Upload -> Process -> Auto-download.

#### 3D Map View (`/3d/`)
*   **Projects**: List of 3D Project models (`.glb` files) placed on a geolocation.
*   **Map**: Cesium-based map visualization (requires API token).

#### Device Tracker (`/tracker/`)
*   **Agent**: Receives heartbeats from client devices (JSON payload).
*   **Dashboard**: Shows online/offline status (Online if seen < 2 mins ago) and hardware stats (CPU, Battery).

#### Server Monitor (`/monitor/`)
*   **Logs**: View detailed HTTP request logs and Error logs.
*   **Export**: Download logs as **CSV** for auditing.

---

## 4. Technical Details

### Technology Stack
*   **Backend**: Python (Django 5.0+)
*   **Database**: PostgreSQL (configured via `settings.py`)
*   **Scheduling/Async**: (Implied) Simple polling APIs used in frontend.

### Permissions System
*   **Superuser**: Global Access.
*   **UserToolAccess**: Custom model linking Users to Tools (`slug` based).
    *   Managed via Admin Dashboard.
    *   Decorators like `@check_tool_access('ticketing')` enforce this in views.

### Configuration
*   **Settings**: `config/settings.py` handles DB, Email, and Timezone.
*   **Static/Media**:
    *   `static/`: CSS/JS assets.
    *   `media/`: User uploads (User photos, Asset 3D models, News attachments).
