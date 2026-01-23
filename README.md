# Office Tools Portal

A comprehensive, commercial-grade web portal for office utilities, built with Django.

## Features
- **Email Signature Generator**: Create professional HTML email signatures.
- **Server Monitor**: Real-time server logs and request tracking.
- **Ticketing System**: Internal support ticket management.
- **News Feed**: Company news and updates.

## Getting Started

### Prerequisites
- Python 3.10+
- pip

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Apply database migrations:
   ```bash
   python manage.py migrate
   ```

4. Create a superuser (admin):
   ```bash
   python manage.py createsuperuser
   ```

5. Run the development server:
   ```bash
   python manage.py runserver
   ```

Access the portal at `http://127.0.0.1:8000/`.

## License
[Your License Here]
