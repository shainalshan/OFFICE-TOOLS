# Deployment Guide: Office Tools Portal

## 1. Project Repository
**URL**: https://github.com/shainalshan/OFFICE-TOOLS

## 2. Credentials
*Make sure to keep this information secure. The system cannot retrieve your existing passwords, so you must define new ones for the new server.*

### GitHub Credentials
*Required to download the code to the server.*
- **Username**: `shainalshan`
- **Password / Personal Access Token**: __________________________

### Server Admin Credentials
*You will create these on the new server during setup.*
- **Admin Username**: __________________________
- **Admin Password**: __________________________

---

## 3. Installation Steps (New Server)

### Step A: Prerequisites
Ensure the server has **Python 3.10+** installed.
Open a terminal (Command Prompt/PowerShell) on the server.

### Step B: Download Code
Run the following command to download your project:
```powershell
git clone https://github.com/shainalshan/OFFICE-TOOLS.git
cd OFFICE-TOOLS
```

### Step C: System Setup
Run these 4 commands in order to set up the environment and database:

1. **Create Virtual Environment**:
   ```powershell
   python -m venv venv
   ```

2. **Activate Environment**:
   ```powershell
   .\venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```

4. **Initialize Database**:
   ```powershell
   python manage.py migrate
   ```

### Step D: Create Admin User
Since the database on the new server is fresh, you need to create a new administrator login:
```powershell
python manage.py createsuperuser
```
*(Follow the prompts to set the Username and Password listed in Section 2)*

### Step E: Start Server
Launch the application:
```powershell
python manage.py runserver 0.0.0.0:8000
```
The portal will be accessible at `http://<your-server-ip>:8000/`.
