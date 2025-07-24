from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from lending.models import Lending
from django.utils import timezone

class Command(BaseCommand):
    help = 'Send email reminders to customers with overdue loans.'

    def handle(self, *args, **options):
        today = timezone.now().date()
        overdue_loans = Lending.objects.filter(status='overdue')
        count = 0
        for loan in overdue_loans:
            customer = loan.customer
            if not customer.email:
                continue
            subject = 'Loan Overdue Reminder'
            message = (
                f'Dear {customer.name},\n\n'
                f'This is a reminder that your loan of amount {loan.amount} is overdue. '
                f'Please make the payment as soon as possible.\n\n'
                f'Due Date: {loan.due_date}\n'
                f'Outstanding Amount: {loan.amount}\n\n'
                'Thank you.'
            )
            try:
                send_mail(
                    subject,
                    message,
                    None,  # Use DEFAULT_FROM_EMAIL
                    [customer.email],
                    fail_silently=False,
                )
                count += 1
                self.stdout.write(self.style.SUCCESS(f'Reminder sent to {customer.email}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Failed to send to {customer.email}: {e}'))
        self.stdout.write(self.style.SUCCESS(f'Total reminders sent: {count}')) 