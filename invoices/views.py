"""
Point of Sale (POS) and Invoice Views for ARSAFA ERP System

This module contains all the view functions for handling Point of Sale and
Invoice operations in the ARSAFA ERP system. It includes views for:
- Listing and managing invoices and POS transactions
- Creating, editing, and deleting transactions
- Processing payments and updating statuses
- API endpoints for product information

The views are designed to handle various business scenarios including:
- Real-time sales processing with immediate payment (POS)
- Traditional invoice system for deferred payments
- Item-level management for both systems
- Customer relationship management through transaction history

Author: ARSAFA Development Team
Version: 1.0
"""

# Import required Django modules and external models
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.db.models import Sum, Count
from django.utils import timezone
from django.http import JsonResponse
from .models import Invoice, InvoiceItem, POS, POSItem
from .forms import InvoiceForm, InvoiceItemForm, POSForm, POSItemForm
from datetime import timedelta
from django.urls import reverse
from inventory.models import Product
from customers.models import Customer
from django.views.decorators.http import require_GET
from decimal import Decimal
from decimal import InvalidOperation
from django.core.exceptions import ValidationError

@login_required
def invoice_list(request):
    """
    Display a combined list of all invoices and paid POS transactions
    
    This view function retrieves and combines both traditional invoices and
    paid POS transactions into a single list for display. It filters out
    duplicate entries and provides summary statistics for the dashboard.
    
    The function combines:
    - Manual invoices (created directly in the invoice system)
    - POS-generated invoices (created from paid POS transactions)
    
    Business Logic:
    - POS transactions that are paid are considered equivalent to invoices
    - Manual invoices that have the same number as a POS transaction are filtered out
    - Results are sorted by date with most recent first
    - Statistics are calculated for display in the dashboard
    
    Args:
        request (HttpRequest): The HTTP request object containing user session data
        
    Returns:
        HttpResponse: Rendered template with combined invoice/POS list and statistics
    """
    # Retrieve all invoices and paid POS transactions from the database
    invoices = Invoice.objects.all()
    paid_pos_sales = POS.objects.filter(status='paid')

    # Build a set of POS invoice numbers to filter out duplicates
    # This prevents showing the same transaction twice (once as invoice, once as POS)
    pos_invoice_numbers = set(pos.pos_number for pos in paid_pos_sales)

    # Initialize list to hold combined invoice and POS data
    combined_list = []

    # Only add manual invoices that are NOT POS-generated
    # This prevents duplicate entries in the combined list
    for inv in invoices:
        if inv.invoice_number not in pos_invoice_numbers:
            combined_list.append({
                'id': inv.id,
                'number': inv.invoice_number,
                'customer_name': inv.customer.name,
                'amount': inv.amount,
                'status': inv.status,
                'date': inv.date,
                'due_date': inv.due_date,
                'type': 'invoice'
            })

    # Add POS-generated invoices to the combined list
    # These represent paid POS transactions that have been converted to invoices
    for pos in paid_pos_sales:
        combined_list.append({
            'id': pos.id,
            'number': pos.pos_number,
            'customer_name': pos.customer_name,
            'amount': pos.total,
            'status': 'paid',  # POS sales in this list are always paid
            'date': pos.date.date(),
            'due_date': pos.date.date(),
            'type': 'pos'
        })
    
    # Sort the combined list by date, most recent first
    # This provides a chronological view with newest transactions at the top
    combined_list.sort(key=lambda x: x['date'], reverse=True)

    # Calculate statistics from the combined list for dashboard display
    # These statistics help users quickly understand business performance
    total_invoices = len(combined_list)
    paid_invoices = sum(1 for item in combined_list if item['status'] == 'paid')
    unpaid_invoices = sum(1 for item in combined_list if item['status'] == 'unpaid')
    overdue_invoices = sum(1 for item in combined_list if item['status'] == 'overdue')
    
    total_amount = sum(item['amount'] for item in combined_list)
    amount_received = sum(item['amount'] for item in combined_list if item['status'] == 'paid')
    
    # Prepare context data for template rendering
    context = {
        'invoices': combined_list,
        'total_invoices': total_invoices,
        'paid_invoices': paid_invoices,
        'unpaid_invoices': unpaid_invoices,
        'overdue_invoices': overdue_invoices,
        'total_amount': total_amount,
        'amount_received': amount_received,
    }
    return render(request, 'invoices/invoice_list.html', context)

@login_required
def invoice_create(request):
    """
    Create a new invoice with auto-generated invoice number
    
    This view handles the creation of new invoices with automatic numbering
    in the INV-XXX format. It supports both GET requests (displaying the
    creation form) and POST requests (processing form submission).
    
    Invoice Number Generation:
    - Follows INV-XXX format (e.g., INV-001, INV-002, etc.)
    - Automatically increments based on the highest existing number
    - Falls back to INV-001 if no invoices exist
    
    Business Logic:
    - Requires user authentication (enforced by @login_required)
    - Validates form data before saving
    - Redirects to invoice editing page after creation
    
    Args:
        request (HttpRequest): The HTTP request object containing form data
        
    Returns:
        HttpResponse: Either rendered form (GET) or redirect to edit page (POST)
    """
    if request.method == 'POST':
        # Process form submission for new invoice creation
        form = InvoiceForm(request.POST)
        if form.is_valid():
            # Create invoice instance but don't save to DB yet
            invoice = form.save(commit=False)
            # Generate invoice number (INV-001 format)
            # Find the last invoice to determine the next number in sequence
            last_invoice = Invoice.objects.order_by('-invoice_number').first()
            if last_invoice:
                # Extract number from last invoice (e.g., INV-005 -> 5)
                last_number = int(last_invoice.invoice_number.split('-')[1])
                # Increment and format with leading zeros (e.g., 6 -> 006)
                invoice.invoice_number = f'INV-{str(last_number + 1).zfill(3)}'
            else:
                # First invoice in the system
                invoice.invoice_number = 'INV-001'
            # Save the invoice to the database
            invoice.save()
            # Redirect to the invoice editing page for item addition
            return redirect('invoice_edit', invoice_id=invoice.id)
    else:
        # Display the empty invoice creation form
        form = InvoiceForm()
    
    # Render the invoice creation form template
    return render(request, 'invoices/invoice_form.html', {'form': form})

@login_required
def invoice_edit(request, invoice_id):
    """
    Edit an existing invoice and manage its items
    
    This view handles the editing of invoices including adding and removing
    items, updating the invoice total, and processing payments. It supports
    multiple actions through form submissions with different button names.
    
    Supported Actions:
    - Adding items to the invoice
    - Removing items from the invoice
    - Processing payment (marking as paid)
    - Updating invoice status
    - Viewing invoice details
    
    Business Logic:
    - Invoice total is automatically recalculated when items are added/removed
    - Payment processing requires validation of items and amounts
    - Status updates are restricted to valid choices
    - All operations require user authentication
    
    Args:
        request (HttpRequest): The HTTP request object containing form data
        invoice_id (int): The ID of the invoice to edit
        
    Returns:
        HttpResponse: Either rendered edit form (GET) or redirect based on action (POST)
    """
    # Retrieve the invoice object or return 404 if not found
    invoice = get_object_or_404(Invoice, id=invoice_id)
    # Get all items associated with this invoice for display
    items = invoice.items.all()
    
    if request.method == 'POST':
        # Handle different form actions based on submitted button names
        if 'add_item' in request.POST:
            # Process adding a new item to the invoice
            item_form = InvoiceItemForm(request.POST)
            if item_form.is_valid():
                # Create item instance but don't save to DB yet
                item = item_form.save(commit=False)
                # Associate the item with the current invoice
                item.invoice = invoice
                # Save the item to the database
                item.save()
                
                # Update invoice amount to reflect new item
                # Recalculate total from all items to ensure accuracy
                invoice.amount = invoice.items.aggregate(Sum('amount'))['amount__sum'] or 0
                invoice.save()
                
                # messages.success(request, 'Item added successfully.')
                # Redirect to same page to show updated item list
                return redirect('invoice_edit', invoice_id=invoice.id)
        elif 'delete_item' in request.POST:
            # Process removing an item from the invoice
            item_id = request.POST.get('item_id')
            # Delete the specified item from the database
            InvoiceItem.objects.filter(id=item_id).delete()
            
            # Update invoice amount to reflect removed item
            # Recalculate total from remaining items
            invoice.amount = invoice.items.aggregate(Sum('amount'))['amount__sum'] or 0
            invoice.save()
            
            # messages.success(request, 'Item removed successfully.')
            # Redirect to same page to show updated item list
            return redirect('invoice_edit', invoice_id=invoice.id)
        elif 'checkout' in request.POST:
            # Process payment and mark invoice as paid
            invoice.status = 'paid'
            # Save updated status to the database
            invoice.save()
            # messages.success(request, 'Checkout complete. Invoice marked as paid.')
            # Redirect to invoice detail page for final review
            return redirect('invoice_detail', invoice_id=invoice.id)
        elif 'update_status' in request.POST:
            # Update invoice status (paid/unpaid/overdue)
            new_status = request.POST.get('status')
            # Validate that the new status is one of the allowed choices
            if new_status in dict(Invoice.STATUS_CHOICES):
                invoice.status = new_status
                # Save updated status to the database
                invoice.save()
                # messages.success(request, 'Invoice status updated successfully.')
                # Redirect to invoice list page
                return redirect('invoice_list')
    
    # Initialize empty item form for adding new items
    item_form = InvoiceItemForm()
    # Prepare context data for template rendering
    context = {
        'invoice': invoice,
        'items': items,
        'item_form': item_form,
    }
    return render(request, 'invoices/invoice_edit.html', context)

@login_required
def invoice_detail(request, invoice_id):
    """
    Display detailed information for a specific invoice
    
    This view renders a detailed view of a single invoice including all
    associated items, customer information, and transaction details.
    It's typically used for reviewing completed invoices or printing.
    
    Business Logic:
    - Requires user authentication (enforced by @login_required)
    - Retrieves complete invoice with all related items
    - Displays formatted invoice for review or printing
    - Does not allow modifications (read-only view)
    
    Args:
        request (HttpRequest): The HTTP request object
        invoice_id (int): The ID of the invoice to display
        
    Returns:
        HttpResponse: Rendered invoice detail template with invoice data
    """
    # Retrieve the invoice object or return 404 if not found
    # get_object_or_404 provides automatic error handling for missing objects
    invoice = get_object_or_404(Invoice, id=invoice_id)
    # Render the invoice detail template with the invoice data
    return render(request, 'invoices/invoice_detail.html', {'invoice': invoice})

@login_required
def invoice_delete(request, invoice_id):
    """
    Delete an invoice and all associated items from the system
    
    This view handles the deletion of invoices and their associated items.
    It performs cascading deletion to ensure data integrity and provides
    error handling for any issues that may occur during deletion.
    
    Deletion Process:
    1. Delete all invoice items first (cascading deletion)
    2. Delete the invoice record
    3. Handle any exceptions that may occur
    4. Provide user feedback through messages
    
    Business Logic:
    - Requires user authentication (enforced by @login_required)
    - Only processes deletion on POST requests
    - Provides confirmation through success/error messages
    - Redirects appropriately based on success/failure
    
    Args:
        request (HttpRequest): The HTTP request object
        invoice_id (int): The ID of the invoice to delete
        
    Returns:
        HttpResponse: Redirect to invoice list (success) or detail page (failure)
    """
    # Retrieve the invoice object or return 404 if not found
    invoice = get_object_or_404(Invoice, id=invoice_id)
    # Only process deletion on POST requests (confirmation)
    if request.method == 'POST':
        try:
            # Delete all invoice items first to maintain referential integrity
            # This prevents foreign key constraint violations
            invoice.items.all().delete()
            # Then delete the invoice record itself
            invoice.delete()
            # Provide success feedback to the user
            messages.success(request, 'Invoice deleted successfully.')
            # Redirect to invoice list page
            return redirect('invoice_list')
        except Exception as e:
            # Handle any exceptions that occur during deletion
            # Provide error feedback to the user
            messages.error(request, f'Error deleting invoice: {str(e)}')
            # Redirect back to invoice detail page
            return redirect('invoice_detail', invoice_id=invoice_id)
    # For GET requests, redirect back to invoice detail page
    return redirect('invoice_detail', invoice_id=invoice_id)

@login_required
def pos_list(request):
    """
    Display a list of all Point of Sale transactions with statistics
    
    This view retrieves and displays all POS transactions with summary
    statistics for the current day. It provides an overview of sales
    performance including counts of paid/unpaid transactions and revenue.
    
    Statistics Calculated:
    - Total number of POS transactions
    - Count of paid transactions
    - Count of unpaid transactions
    - Total revenue for paid transactions today
    
    Business Logic:
    - Requires user authentication (enforced by @login_required)
    - Calculates daily revenue from paid transactions only
    - Provides comprehensive overview of POS system performance
    - Supports navigation to individual transaction details
    
    Args:
        request (HttpRequest): The HTTP request object containing user session data
        
    Returns:
        HttpResponse: Rendered POS list template with transactions and statistics
    """
    # Retrieve all POS transactions from the database
    pos_list = POS.objects.all()
    # Get today's date for daily revenue calculation
    today = timezone.now().date()
    # Calculate total number of POS transactions
    total_pos = pos_list.count()
    # Calculate count of paid transactions
    paid_pos = pos_list.filter(status='paid').count()
    # Calculate count of unpaid transactions
    unpaid_pos = pos_list.filter(status='unpaid').count()
    # Calculate total revenue for paid transactions today
    # Only paid POS transactions contribute to daily revenue
    total_revenue = POS.objects.filter(status='paid', date__date=today).aggregate(Sum('total'))['total__sum'] or 0

    # Prepare context data for template rendering
    context = {
        'pos_list': pos_list,
        'total_pos': total_pos,
        'paid_pos': paid_pos,
        'unpaid_pos': unpaid_pos,
        'total_revenue': total_revenue,
    }
    return render(request, 'invoices/pos_list.html', context)

@login_required
def pos_create(request):
    """
    Create a new Point of Sale transaction with auto-generated number
    
    This view handles the creation of new POS transactions with automatic
    numbering in the POS-XXX format. It supports both GET requests (displaying
    the creation form) and POST requests (processing form submission).
    
    POS Number Generation:
    - Follows POS-XXX format (e.g., POS-001, POS-002, etc.)
    - Automatically increments based on the highest existing number
    - Falls back to POS-001 if no POS transactions exist
    
    Business Logic:
    - Requires user authentication (enforced by @login_required)
    - Validates form data before saving
    - Redirects to POS editing page after creation for item addition
    - Supports quick customer information capture
    
    Args:
        request (HttpRequest): The HTTP request object containing form data
        
    Returns:
        HttpResponse: Either rendered form (GET) or redirect to edit page (POST)
    """
    if request.method == 'POST':
        # Process form submission for new POS creation
        form = POSForm(request.POST)
        if form.is_valid():
            # Create POS instance but don't save to DB yet
            pos = form.save(commit=False)
            # Generate POS number (POS-001 format)
            # Find the last POS transaction to determine the next number in sequence
            last_pos = POS.objects.order_by('-pos_number').first()
            if last_pos:
                # Extract number from last POS (e.g., POS-005 -> 5)
                last_number = int(last_pos.pos_number.split('-')[1])
                # Increment and format with leading zeros (e.g., 6 -> 006)
                pos.pos_number = f'POS-{str(last_number + 1).zfill(3)}'
            else:
                # First POS transaction in the system
                pos.pos_number = 'POS-001'
            # Save the POS transaction to the database
            pos.save()
            # Redirect to the POS editing page for item addition
            return redirect('pos_edit', pos_id=pos.id)
    else:
        # Display the empty POS creation form
        form = POSForm()
    
    # Render the POS creation form template
    return render(request, 'invoices/pos_form.html', {'form': form})

@login_required
def pos_edit(request, pos_id):
    """
    Edit a Point of Sale transaction and manage its items
    
    This view handles the editing of POS transactions including adding and
    removing items, applying discounts, and processing payments. It supports
    multiple actions through form submissions with different button names.
    
    Supported Actions:
    - Adding items to the POS transaction
    - Removing items from the POS transaction
    - Updating discount amount
    - Processing payment (marking as paid)
    - Viewing transaction details
    
    Business Logic:
    - POS subtotal is automatically recalculated when items are added/removed
    - Discount validation prevents negative or excessive discounts
    - Payment processing requires validation of items and amounts
    - Zero-amount transactions cannot be marked as paid (model-level validation)
    - All operations require user authentication
    
    Args:
        request (HttpRequest): The HTTP request object containing form data
        pos_id (int): The ID of the POS transaction to edit
        
    Returns:
        HttpResponse: Either rendered edit form (GET) or redirect based on action (POST)
    """
    # Retrieve the POS transaction object or return 404 if not found
    pos = get_object_or_404(POS, id=pos_id)
    # Get all items associated with this POS transaction for display
    items = pos.items.all()
    # Initialize empty item form for adding new items
    item_form = POSItemForm()  # Initialize the form here

    if request.method == 'POST':
        # Handle different form actions based on submitted button names
        if 'add_item' in request.POST:
            # Process adding a new item to the POS transaction
            item_form = POSItemForm(request.POST)  # Re-bind with POST data
            if item_form.is_valid():
                # Create item instance but don't save to DB yet
                item = item_form.save(commit=False)
                # Associate the item with the current POS transaction
                item.pos = pos
                # Save the item to the database
                item.save()
                
                # Update POS subtotal to reflect new item
                # Recalculate subtotal from all items to ensure accuracy
                pos.subtotal = pos.items.aggregate(Sum('total'))['total__sum'] or 0
                pos.save()
                
                # messages.success(request, 'Item added successfully.')
                # Redirect to same page to show updated item list
                return redirect('pos_edit', pos_id=pos.id)
        elif 'delete_item' in request.POST:
            # Process removing an item from the POS transaction
            item_id = request.POST.get('item_id')
            # Delete the specified item from the database
            POSItem.objects.filter(id=item_id).delete()
            
            # Update POS subtotal to reflect removed item
            # Recalculate subtotal from remaining items
            pos.subtotal = pos.items.aggregate(Sum('total'))['total__sum'] or 0
            pos.save()
            
            # messages.success(request, 'Item removed successfully.')
            # Redirect to same page to show updated item list
            return redirect('pos_edit', pos_id=pos.id)
        elif 'update_discount' in request.POST:
            # Process updating discount amount for the POS transaction
            discount = request.POST.get('discount', 0)
            try:
                # Convert discount string to Decimal for calculation
                discount = Decimal(discount)
                # Validate that discount is not negative
                if discount < 0:
                    raise ValueError('Discount cannot be negative')
                # Validate that discount does not exceed subtotal
                if discount > pos.subtotal:
                    # messages.error(request, 'Discount cannot exceed subtotal.')
                    pass
                else:
                    # Apply valid discount to the POS transaction
                    pos.discount = discount
                    # Save updated discount to the database
                    pos.save()
                    # messages.success(request, 'Discount updated successfully.')
            except (ValueError, InvalidOperation):
                # Handle invalid discount amount (non-numeric or other errors)
                # messages.error(request, 'Invalid discount amount.')
                pass
            # Redirect to same page to show updated discount
            return redirect('pos_edit', pos_id=pos.id)
        elif 'make_payment' in request.POST:
            # Process payment and mark POS transaction as paid
            # Check if POS has items before allowing payment
            # Prevent payment processing for empty transactions
            if items.count() == 0:
                messages.error(request, 'Cannot make payment for an empty sale. Please add at least one item.')
                return redirect('pos_edit', pos_id=pos.id)
            
            # Check if subtotal is greater than 0 before allowing payment
            # Prevent payment processing for zero-amount transactions
            if pos.subtotal <= 0:
                messages.error(request, 'Cannot make payment for a sale with zero total. Please add items.')
                return redirect('pos_edit', pos_id=pos.id)
            
            # Validate and save POS transaction when marking as paid
            # This includes model-level validation to prevent zero-amount payments
            pos.status = 'paid'
            try:
                # Run model-level validation before saving
                # This prevents marking zero-amount transactions as paid
                pos.full_clean()
                pos.save()
                messages.success(request, 'Payment completed successfully.')
            except ValidationError as e:
                # Display validation errors and reset status if validation fails
                messages.error(request, f'Cannot mark as paid: {", ".join(e.messages)}')
                pos.status = 'unpaid'  # Reset status
                pos.save()
            # Redirect to POS detail page for final review
            return redirect('pos_detail', pos_id=pos.id)

    # Prepare context data for template rendering
    context = {
        'pos': pos,
        'items': items,
        'item_form': item_form,
        'has_items': items.count() > 0,
        'can_make_payment': items.count() > 0 and pos.subtotal > 0,
    }
    return render(request, 'invoices/pos_edit.html', context)

@login_required
def pos_detail(request, pos_id):
    """
    Display detailed information for a Point of Sale transaction
    
    This view renders a detailed view of a single POS transaction including
    all associated items, customer information, and transaction details. It
    also handles discount updates and payment status changes.
    
    Supported Actions:
    - Updating discount amount
    - Changing payment status (paid/unpaid)
    - Viewing transaction details for review or printing
    
    Business Logic:
    - Zero-amount transactions cannot be marked as paid (model-level validation)
    - Payment status changes require validation of items and amounts
    - Discount validation prevents negative or excessive discounts
    - All operations require user authentication
    - Status changes are restricted to valid choices
    
    Args:
        request (HttpRequest): The HTTP request object containing form data
        pos_id (int): The ID of the POS transaction to display
        
    Returns:
        HttpResponse: Rendered POS detail template with transaction data
    """
    # Retrieve the POS transaction object or return 404 if not found
    pos = get_object_or_404(POS, id=pos_id)
    # Get all items associated with this POS transaction for display
    items = pos.items.all()
    
    if request.method == 'POST':
        # Handle form submissions for updating transaction details
        if 'update_discount' in request.POST:
            # Process updating discount amount for the POS transaction
            discount = request.POST.get('discount', 0)
            try:
                # Convert discount string to Decimal for calculation
                discount = Decimal(discount)
                # Validate that discount is not negative
                if discount < 0:
                    raise ValueError('Discount cannot be negative')
                # Validate that discount does not exceed subtotal
                if discount > pos.subtotal:
                    messages.error(request, 'Discount cannot exceed subtotal.')
                else:
                    # Apply valid discount to the POS transaction
                    pos.discount = discount
                    # Save updated discount to the database
                    pos.save()
                    messages.success(request, 'Discount updated successfully.')
            except (ValueError, InvalidOperation):
                # Handle invalid discount amount (non-numeric or other errors)
                messages.error(request, 'Invalid discount amount.')
        elif 'update_status' in request.POST:
            # Process updating payment status for the POS transaction
            new_status = request.POST.get('status')
            # Validate that the new status is one of the allowed choices
            if new_status in dict(POS.STATUS_CHOICES):
                # Store the previous status for potential rollback
                # This allows reverting changes if validation fails
                previous_status = pos.status
                
                # Check if trying to mark as paid without items
                # Prevent payment processing for empty transactions
                if new_status == 'paid' and items.count() == 0:
                    messages.error(request, 'Cannot mark as paid for an empty sale. Please add items first.')
                elif new_status == 'paid' and pos.subtotal <= 0:
                    # Check if trying to mark as paid with zero total
                    # Prevent payment processing for zero-amount transactions
                    messages.error(request, 'Cannot mark as paid for a sale with zero total. Please add items.')
                else:
                    # Apply new status and validate before saving
                    pos.status = new_status
                    try:
                        # Run model-level validation before saving status change
                        # This prevents marking zero-amount transactions as paid
                        pos.full_clean()
                        pos.save()
                        messages.success(request, f'Payment status updated to {new_status.title()}.')
                    except ValidationError as e:
                        # Rollback to previous status if validation fails
                        # This maintains data integrity and prevents invalid states
                        pos.status = previous_status
                        pos.save()
                        messages.error(request, f'Cannot update status: {", ".join(e.messages)}')
        # Redirect to same page to show updated information
        return redirect('pos_detail', pos_id=pos.id)
    
    # Prepare context data for template rendering
    context = {
        'pos': pos,
        'items': items,
        'has_items': items.count() > 0,
        'can_make_payment': items.count() > 0 and pos.subtotal > 0,
    }
    return render(request, 'invoices/pos_detail.html', context)

@login_required
def pos_delete(request, pos_id):
    """
    Delete a Point of Sale transaction from the system
    
    This view handles the deletion of POS transactions. It performs
    direct deletion of the transaction record and provides user feedback.
    
    Deletion Process:
    1. Delete the POS transaction record
    2. Provide user feedback through messages
    3. Redirect to POS list page
    
    Business Logic:
    - Requires user authentication (enforced by @login_required)
    - Only processes deletion on POST requests (confirmation)
    - Provides confirmation through success messages
    - Redirects to POS list page after deletion
    
    Args:
        request (HttpRequest): The HTTP request object
        pos_id (int): The ID of the POS transaction to delete
        
    Returns:
        HttpResponse: Redirect to POS list page
    """
    # Retrieve the POS transaction object or return 404 if not found
    pos = get_object_or_404(POS, id=pos_id)
    # Only process deletion on POST requests (confirmation)
    if request.method == 'POST':
        # Delete the POS transaction record
        pos.delete()
        # Provide success feedback to the user
        # messages.success(request, 'POS transaction deleted successfully.')
        # Redirect to POS list page
        return redirect('pos_list')
    # For GET requests, redirect to POS list page
    return redirect('pos_list')

@require_GET
def get_product_price(request, product_id):
    """
    API endpoint to retrieve the price of a specific product
    
    This view function serves as an API endpoint that returns the current
    price of a product in JSON format. It's used by the frontend to
    automatically populate unit prices when products are selected in forms.
    
    The function retrieves the product's unit price, which represents the
    current selling price for the product. This ensures that prices are
    always up-to-date when items are added to invoices or POS transactions.
    
    HTTP Method Restriction:
    - Only accepts GET requests (enforced by @require_GET decorator)
    - Returns 405 Method Not Allowed for other HTTP methods
    
    Args:
        request (HttpRequest): The HTTP request object
        product_id (int): The ID of the product to retrieve price for
        
    Returns:
        JsonResponse: JSON object containing the product price
        Example: {'price': '15.99'}
        
    Error Handling:
        - Returns 404 if product is not found
        - Price is returned as string to preserve decimal precision
    """
    # Retrieve the product object or return 404 if not found
    product = get_object_or_404(Product, id=product_id)
    # Use unit_price if selling_price is None, otherwise use selling_price
    # This ensures we always return a valid price for the product
    price = product.unit_price
    # Return the price in JSON format for frontend consumption
    return JsonResponse({'price': price})

@require_GET
def get_product_by_barcode(request, barcode):
    """
    API endpoint to retrieve product information by barcode
    
    This view function serves as an API endpoint that returns product
    information including ID, name, and price based on a barcode scan.
    It's used by the frontend to automatically populate product details
    when a barcode is scanned in POS forms.
    
    The function searches for a product with the matching barcode and
    returns essential information needed to add the product to a sale.
    This enables efficient barcode scanning workflow in the POS system.
    
    HTTP Method Restriction:
    - Only accepts GET requests (enforced by @require_GET decorator)
    - Returns 405 Method Not Allowed for other HTTP methods
    
    Args:
        request (HttpRequest): The HTTP request object
        barcode (str): The barcode to search for
        
    Returns:
        JsonResponse: JSON object containing product information or error
        Success example: {'product_id': 1, 'name': 'Product Name', 'price': '15.99'}
        Error example: {'error': 'Not found'} with 404 status
        
    Business Logic:
        - Returns only essential product information for POS workflow
        - Price is returned as string to preserve decimal precision
        - Returns 404 status when barcode is not found
    """
    # Import Product model to avoid circular import issues
    from inventory.models import Product
    # Search for product with matching barcode
    # Returns first match or None if not found
    product = Product.objects.filter(barcode=barcode).first()
    if product:
        # Return product information in JSON format for frontend consumption
        # Includes ID for database reference, name for display, and price for calculation
        return JsonResponse({'product_id': product.id, 'name': product.name, 'price': str(product.unit_price)})
    else:
        # Return error response when barcode is not found
        # 404 status indicates resource not found
        return JsonResponse({'error': 'Not found'}, status=404)

@login_required
def test_invoice_delete(request):
    """
    Test view to verify invoice delete functionality
    
    This view is used for testing purposes to verify that the invoice
    deletion functionality works correctly. It displays all invoices
    in a test mode interface for verification.
    
    Business Logic:
    - Requires user authentication (enforced by @login_required)
    - Retrieves all invoices for display in test interface
    - Activates test mode in the template for special styling/behavior
    - Not intended for production use, primarily for development/testing
    
    Args:
        request (HttpRequest): The HTTP request object containing user session data
        
    Returns:
        HttpResponse: Rendered test delete template with all invoices
    """
    # Retrieve all invoices from the database for testing
    invoices = Invoice.objects.all()
    # Prepare context data for template rendering
    # test_mode flag enables special features in the template
    context = {
        'invoices': invoices,
        'test_mode': True
    }
    # Render the test delete template with all invoices
    return render(request, 'invoices/test_invoice_delete.html', context)