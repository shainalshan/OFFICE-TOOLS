# Windows Server Deployment Guide for Office Tools

This guide explains how to deploy the Office Tools application on a Windows Server using **IIS (Internet Information Services)** and **PostgreSQL**.

## Prerequisites
1.  **Windows Server** (2016, 2019, or 2022).
2.  **Administrator Access** to the server.
3.  **Internet Connection** on the server (for downloading Python, PostgreSQL, and dependencies).

---

## 1. Install System Requirements

### Step A: Install Python
1.  Download [Python 3.10+](https://www.python.org/downloads/windows/).
2.  Run the installer. **IMPORTANT**: Check the box **"Add Python to PATH"**.
3.  Select "Install Now".

### Step B: Install PostgreSQL
1.  Download [PostgreSQL for Windows](https://www.enterprisedb.com/downloads/postgres-postgresql-downloads).
2.  Run the installer. Use default settings.
3.  **Remember the password** you set for the `postgres` superuser.
4.  Launch **pgAdmin 4** (installed with PostgreSQL) and create a new database named `office_tools_db`.

### Step C: Enable IIS
1.  Open **Server Manager** -> **Manage** -> **Add Roles and Features**.
2.  Select **Web Server (IIS)**.
3.  Under **Role Services**, ensure **CGI** (under Application Development) is selected.
4.  Complete the installation.

---

## 2. Download and Configure the Application

### Step A: Clone Repository
1.  Open PowerShell as Administrator.
2.  Navigate to `C:\inetpub\wwwroot` (or your preferred folder).
    ```powershell
    cd C:\inetpub\wwwroot
    git clone https://github.com/shainalshan/OFFICE-TOOLS.git
    ```
    *Note: You may need to install Git first: used [Git for Windows](https://git-scm.com/download/win).*

### Step B: Setup Virtual Environment & Dependencies
1.  Navigate into the project folder:
    ```powershell
    cd OFFICE-TOOLS
    ```
2.  Install dependencies directly to Python (easier for IIS) OR use a virtual environment. *For this guide, we will use Global Python for simplicity with IIS.*
    ```powershell
    pip install -r requirements.txt
    pip install wfastcgi
    ```
3.  Enable wfastcgi:
    ```powershell
    wfastcgi-enable
    ```
    *Copy the path output by this command (e.g., `c:\python310\python.exe|c:\python310\lib\site-packages\wfastcgi.py`). You will need it for `web.config`.*

### Step C: Configure Database & Static Files
1.  Run migrations to setup the database:
    *Ensure PostgreSQL is running and your `web.config` or environment variables match your DB Credentials.*
    ```powershell
    $env:DB_NAME="office_tools_db"
    $env:DB_USER="postgres"
    $env:DB_PASSWORD="your_postgres_password"
    python manage.py migrate
    ```
2.  Collect static files:
    ```powershell
    python manage.py collectstatic
    ```
    *Type `yes` when prompted.*

3.  Create Superuser:
    ```powershell
    python manage.py createsuperuser
    ```

---

## 3. Configure IIS

### Step A: Verify web.config
A `web.config` file has been created in your project root. Open it and check:
1.  **scriptProcessor**: Ensure it matches the output from `wfastcgi-enable`.
2.  **PYTHONPATH**: Update to your actual project path (e.g., `C:\inetpub\wwwroot\OFFICE-TOOLS`).
3.  **DB_PASSWORD**: Update with your actual PostgreSQL password.

### Step B: Add Site to IIS
1.  Open **IIS Manager**.
2.  Right-click **Sites** -> **Add Website**.
    -   **Site name**: OfficeTools
    -   **Physical path**: `C:\inetpub\wwwroot\OFFICE-TOOLS`
    -   **Port**: 80 (or 8000 if you want to keep Default Web Site).
3.  **Permissions**:
    -   Right-click the `OFFICE-TOOLS` folder in File Explorer -> Properties -> Security.
    -   Add `IIS AppPool\OfficeTools` (replace OfficeTools with your App Pool name if different) or simply give `Everyone` Read/Write access (easier but less secure) just to test.
    -   *Better approach:* Give `IIS_IUSRS` Read & Execute permissions. Give Modify permissions to the `db.sqlite3` file (if using SQLite) or `media` folder.

### Step C: Restart IIS
1.  Select your site in IIS Manager.
2.  Click **Restart** on the right panel.
3.  Browse to `http://localhost/` (or your server IP).

---

## Troubleshooting
- **500 Error**: Check `C:\inetpub\wwwroot\OFFICE-TOOLS\django_errors.log` (if configured) or enable `stdoutLogEnabled="true"` in `web.config`.
- **Static Files Missing**: Ensure `python manage.py collectstatic` was successful and IIS has permission to read the `staticfiles` folder.
