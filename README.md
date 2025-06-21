# ARSAFA SOLUTION

A Django-based inventory management system with admin login, inventory tracking, sales, invoicing, customer management, lending, email reminders, and analytics dashboard.

## Features
- Admin Login (secure authentication)
- Inventory Management (CRUD, alerts)
- Sales Tracking (reports, graphs)
- Invoicing (PDF, print)
- Customer Module (credit, history)
- Lending Module (buy now, pay later)
- Email Reminders (overdue, customizable)
- Admin Dashboard (analytics, quick stats)

## Tech Stack
- **Frontend:** HTML, CSS, Bootstrap
- **Backend:** Django (Python)
- **Database:** SQLite
- **Visualization:** Chart.js (CDN)

## Setup Instructions
1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd IMS
   ```
2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Apply migrations:**
   ```bash
   python manage.py migrate
   ```
5. **Create a superuser:**
   ```bash
   python manage.py createsuperuser
   ```
6. **Run the development server:**
   ```bash
   python manage.py runserver
   ```
7. **Access the app:**
   Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser.

## Folder Structure
- `ims/` - Django project settings
- `accounts/` - Admin login & authentication
- `inventory/` - Product & stock management
- `sales/` - Sales tracking & invoicing
- `customers/` - Customer & lending management
- `dashboard/` - Analytics & dashboard

## License
MIT 