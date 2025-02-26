from celery import shared_task
from .models import MaintenanceReminder
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
from django.urls import reverse
from django.template.loader import render_to_string

@shared_task
def check_maintenance_reminders():
    """
    Check all maintenance reminders and update their status based on due date and mileage.
    Send email notifications for reminders that are due soon or overdue.
    """
    today = timezone.now().date()
    due_soon_threshold = today + timedelta(days=14)

    # Get all active reminders
    reminders = MaintenanceReminder.objects.filter(status__in=['pending', 'due_soon', 'overdue'])

    for reminder in reminders:
        old_status = reminder.status

        # Check due date
        if reminder.due_date:
            if reminder.due_date <= today:
                reminder.status = 'overdue'
            elif reminder.due_date <= due_soon_threshold:
                reminder.status = 'due_soon'

        # Check mileage
        if reminder.due_mileage and reminder.due_mileage <= reminder.vehicle.current_mileage:
            reminder.status = 'overdue'

        # If status changed, save the reminder and notify the user
        if old_status != reminder.status:
            reminder.save()

            # Only send notification if status got worse (pending -> due_soon, or anything -> overdue)
            if ((old_status == 'pending' and reminder.status == 'due_soon') or
                (reminder.status == 'overdue' and old_status != 'overdue')):
                send_reminder_notification.delay(reminder.id)

    return f"Checked {reminders.count()} maintenance reminders"

@shared_task
def send_reminder_notification(reminder_id):
    """Send a notification email for a specific reminder"""
    try:
        reminder = MaintenanceReminder.objects.get(id=reminder_id)
        user = reminder.vehicle.user

        subject = f"Maintenance Reminder: {reminder.category.name} for your {reminder.vehicle}"

        # Create context for the email template
        context = {
            'user': user,
            'reminder': reminder,
            'vehicle': reminder.vehicle,
            'status': reminder.status,
            'app_url': settings.SITE_URL if hasattr(settings, 'SITE_URL') else 'http://localhost:8000',
            'reminder_url': reverse('reminder-list')
        }

        # Render email template with context
        html_message = render_to_string('maintenance/email/reminder_notification.html', context)
        plain_message = render_to_string('maintenance/email/reminder_notification.txt', context)

        # Send the email
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False
        )

        return f"Sent notification for reminder {reminder_id}"
    except MaintenanceReminder.DoesNotExist:
        return f"Reminder {reminder_id} not found"
    except Exception as e:
        return f"Error sending notification: {str(e)}"
