# ARSAFA SOLUTION

A complete business management system built with Django for small and medium businesses. It helps manage daily tasks such as inventory, sales, POS, invoices, customers, employees, lending, repayment reminders, business notes, and barcode scanning — all in one place.

---

## Features

- **Admin Dashboard**: Get a quick overview of sales, inventory, low stock & nearly expiry alerts, and other key business stats in one place
- **Inventory Management**: Add, modify, search, and organize products by category, monitor stock levels, track expiry dates, and check total inventory valuation.
- **Sales & POS**: Handle sales and POS transactions (both paid and unpaid), with access to complete sales history.
- **Invoicing**: Easily create, edit, and track invoices with payment status and due dates.
- **Customer Management**: Keep customer details, purchase history, total sales, and activity records organized. This will help us to implement the loyalty program later on.
- **Employee Management**: Store and manage employee details, roles, and system access.
- **Lending Module**: Manage customer loans, including interest rates, repayment schedules, and due dates.
- **Email Reminders**: Automatically send reminders for overdue invoices and unpaid loans.
- **Notes**: Create, edit, and delete personal notes, accessible from both the navigation bar and dashboard quick links.
- **Barcode Scanner**: Quickly add products to inventory or select them at POS using barcode scanning.
- **Sales & Reporting**: Visualize sales and inventory insights with interactive charts powered by Chart.js (via CDN).
- **Data Management**: Use admin commands to clear/reset data for testing or new deployments.

---

## Detailed Feature Overview

### 1. Admin Dashboard
- **Centralized Overview:** See key business metrics at a glance: today’s sales, low stock items, pending invoices, credit balances, and recent activities.
- **Quick Navigation:** Access all major modules (Inventory, Sales, POS, Invoices, Customers, Lending, Employees) from dashboard cards.
- **Recent Activities Feed:** Instantly view the latest actions (new invoices, payments, stock updates, new customers) for fast decision-making.
- **Data Reset:** Admins can clear all business data (for testing or new deployments) with a single action.

![alt_text](https://github.com/KHANDAKERALIARIYAN/ARSAFA___Solution/blob/ad4dc7a55f519e18de2480e1713794823a189d25/readme-assets/admin-dashboard.png)

### 2. Inventory Management
- **Product Catalog:** Add, edit, and delete products with details like name, category, quantity, unit price, buying price, expiry date, input date, and barcode.
- **Search, Filter, and Sort:** Find products quickly by name, category, or sort by price, expiry, or stock level.
- **Low Stock Alerts:** Products below a configurable quantity threshold are highlighted and counted, helping prevent stockouts.
- **Expiry Alerts:** Products nearing expiry (within 7 days) are flagged for timely action.
- **Bulk Operations:** Use management commands to add random products or update product statuses in bulk.
- **Admin Panel Integration:** Manage products via Django admin with advanced search and filtering.

### 3. Sales & POS (Point of Sale)
- **Sales Analytics Dashboard:** Visualize total sales, orders, paid/unpaid amounts, daily/weekly sales trends, and top-selling products.
- **POS Transactions:** Create and manage sales directly at the point of sale, supporting both paid and unpaid transactions.
- **Order Management:** Track all sales and POS orders, including detailed product breakdowns and customer associations.
- **Top Products & Trends:** Identify best-selling products and monitor sales growth with interactive charts.
- **Test Data Management:** Easily clear sales data for testing or demonstration purposes.

### 4. Invoicing
- **Invoice List & Filtering:** View all invoices (manual and POS-generated), filter by status (paid, unpaid, overdue), and search by customer or number.
- **Create/Edit Invoices:** Generate invoices for customers, set due dates, and update details as needed.
- **POS Integration:** POS transactions automatically generate corresponding invoices for seamless accounting.
- **Payment Tracking:** Mark invoices as paid/unpaid, update statuses, and track due dates to manage cash flow.
- **API Endpoints:** Fetch product prices and details by barcode for fast POS operations.
- **Bulk Deletion:** Use management commands to clear invoice data in bulk.

### 5. Customer Management
- **Customer Directory:** Add, edit, and delete customer records with contact info, purchase history, and outstanding balances.
- **Purchase & Balance Tracking:** Automatically aggregate all POS sales for each customer and update their outstanding balances.
- **Outstanding Balances:** Instantly see which customers owe money and how much, with automatic updates from unpaid POS transactions.
- **Activity Log:** Track each customer’s last purchase date and total purchases.
- **Data Integrity Tools:** Management commands to check, fix, or clear customer data, ensuring accuracy.

### 6. Lending Module
- **Lending Dashboard:** Overview of all lending records, including active, repaid, and overdue loans.
- **Add/Edit Lending Records:** Create or update loans for customers, set interest rates, due dates, and add notes.
- **Repayment & Overdue Tracking:** Mark loans as repaid or overdue, and monitor outstanding amounts.
- **Auto-Lending:** Unpaid POS transactions automatically create or update lending records for the customer.
- **Cleanup & Verification:** Management commands to clean up or verify lending records based on unpaid POS bills.

### 7. Employee Management
- **Employee Directory:** Add, edit, and delete employee records, including name, NID, designation, phone, salary, and joining date.
- **Admin Panel Integration:** Manage employees via Django admin for advanced control.

### 8. Data Visualization
- **Interactive Charts:** Use Chart.js (via CDN) to visualize sales trends, product performance, and revenue growth.
- **Summary Cards:** See key metrics in visually appealing cards for quick insights.

### 9. Email Reminders *(Planned/Optional)*
- **Automated Reminders:** Send email notifications for overdue invoices and lending repayments (planned feature).

### 10. Data Management & Utilities
- **Management Commands:** Use Django’s command-line tools to add random data, clear/reset modules, and maintain data integrity.
- **Bulk Operations:** Perform large-scale updates or deletions efficiently for testing or new deployments.

### 11. Notes
- **Create, View, Edit, Delete Notes:** Add personal notes for reminders, ideas, or tasks. Each note has a title, content, and timestamps.
- **Table View:** All notes are displayed in a sortable table with quick action icons for view, edit, and delete.
- **Universal Access:** Access the Notes feature from the main navigation bar or the admin dashboard quick access section.
- **User-Friendly:** Clean interface for managing notes efficiently alongside other business modules.

---

## Folder Structure
```
accounts/      # User authentication, admin dashboard, base templates
inventory/     # Product models, inventory views, forms, and templates
sales/         # Sales and POS models, analytics, and reporting
invoices/      # Invoice and POS management, templates, and APIs
customers/     # Customer models, forms, dashboards, and utilities
lending/       # Lending models, forms, and dashboards
employees/     # Employee management
ARSAFA___SOLUTION/ # Project settings, URLs, WSGI/ASGI
staticfiles/   # Static assets (CSS, JS, images)
manage.py      # Django management script
requirements.txt # Python dependencies
```

## Setup Instructions
1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd ARSAFA___Solution
   ```
2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # On Windows
   # Or
   source venv/bin/activate  # On Mac/Linux
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

## Tech Stack
- **Frontend:** HTML, CSS, Bootstrap, JavaScript
- **Backend:** Django (Python)
- **Database:** SQLite (default, can be changed)
- **Visualization:** Chart.js (CDN)
- **PDF Generation:** xhtml2pdf

## Contributors
- Khandaker Ali Ariyan
- Nayef Wasit Siddiqui
- Samiun Alim Auntor

## License
MIT 
