from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import MaintenanceRecord, MaintenanceReminder, CostEstimate
from vehicles.models import Vehicle
from .forms import MaintenanceRecordForm, MaintenanceReminderForm
from django.utils import timezone

@login_required
def maintenance_list(request):
    # Get all maintenance records for the user's vehicles
    records = MaintenanceRecord.objects.filter(
        vehicle__user=request.user
    ).order_by('-service_date')

    # Optional filtering by vehicle
    vehicle_id = request.GET.get('vehicle')
    if vehicle_id:
        records = records.filter(vehicle_id=vehicle_id)

    # Get user's vehicles for the filter dropdown
    vehicles = Vehicle.objects.filter(user=request.user)

    context = {
        'records': records,
        'vehicles': vehicles,
        'selected_vehicle': vehicle_id
    }
    return render(request, 'maintenance/maintenance_list.html', context)

@login_required
def maintenance_detail(request, pk):
    record = get_object_or_404(MaintenanceRecord, pk=pk, vehicle__user=request.user)

    # Get cost estimates for this type of maintenance
    estimates = CostEstimate.objects.filter(
        category=record.category,
        make__iexact=record.vehicle.make,
        year_start__lte=record.vehicle.year,
        year_end__gte=record.vehicle.year
    ).first()

    context = {
        'record': record,
        'cost_estimate': estimates
    }
    return render(request, 'maintenance/maintenance_detail.html', context)

@login_required
def maintenance_create(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, pk=vehicle_id, user=request.user)

    if request.method == 'POST':
        form = MaintenanceRecordForm(request.POST, request.FILES, vehicle=vehicle)
        if form.is_valid():
            record = form.save(commit=False)
            record.vehicle = vehicle

            # Set estimated cost if available
            if hasattr(form, 'estimated_cost'):
                record.estimated_cost = form.estimated_cost

            record.save()

            messages.success(request, 'Maintenance record added successfully!')
            return redirect('vehicle-detail', pk=vehicle.pk)
    else:
        form = MaintenanceRecordForm(
            vehicle=vehicle,
            initial={'mileage_at_service': vehicle.current_mileage, 'service_date': timezone.now().date()}
        )

    return render(request, 'maintenance/maintenance_form.html', {
        'form': form,
        'vehicle': vehicle,
        'title': 'Add Maintenance Record'
    })

@login_required
def maintenance_update(request, pk):
    record = get_object_or_404(MaintenanceRecord, pk=pk, vehicle__user=request.user)
    vehicle = record.vehicle

    if request.method == 'POST':
        form = MaintenanceRecordForm(request.POST, request.FILES, instance=record, vehicle=vehicle)
        if form.is_valid():
            form.save()
            messages.success(request, 'Maintenance record updated successfully!')
            return redirect('maintenance-detail', pk=record.pk)
    else:
        form = MaintenanceRecordForm(instance=record, vehicle=vehicle)

    return render(request, 'maintenance/maintenance_form.html', {
        'form': form,
        'vehicle': vehicle,
        'record': record,
        'title': 'Update Maintenance Record'
    })

@login_required
def maintenance_delete(request, pk):
    record = get_object_or_404(MaintenanceRecord, pk=pk, vehicle__user=request.user)
    vehicle = record.vehicle

    if request.method == 'POST':
        record.delete()
        messages.success(request, 'Maintenance record deleted successfully!')
        return redirect('vehicle-detail', pk=vehicle.pk)

    return render(request, 'maintenance/maintenance_confirm_delete.html', {
        'record': record
    })

@login_required
def reminder_list(request):
    # Get all reminders for the user's vehicles
    reminders = MaintenanceReminder.objects.filter(
        vehicle__user=request.user
    ).order_by('status', 'due_date')

    # Optional filtering by vehicle or status
    vehicle_id = request.GET.get('vehicle')
    status = request.GET.get('status')

    if vehicle_id:
        reminders = reminders.filter(vehicle_id=vehicle_id)

    if status:
        reminders = reminders.filter(status=status)

    # Get user's vehicles for the filter dropdown
    vehicles = Vehicle.objects.filter(user=request.user)

    # Count reminders by status
    status_counts = {
        'all': reminders.count(),
        'pending': reminders.filter(status='pending').count(),
        'due_soon': reminders.filter(status='due_soon').count(),
        'overdue': reminders.filter(status='overdue').count(),
        'completed': reminders.filter(status='completed').count(),
    }

    context = {
        'reminders': reminders,
        'vehicles': vehicles,
        'selected_vehicle': vehicle_id,
        'selected_status': status,
        'status_counts': status_counts
    }
    return render(request, 'maintenance/reminder_list.html', context)

@login_required
def reminder_create(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, pk=vehicle_id, user=request.user)

    if request.method == 'POST':
        form = MaintenanceReminderForm(request.POST, vehicle=vehicle)
        if form.is_valid():
            reminder = form.save(commit=False)
            reminder.vehicle = vehicle

            # Check for cost estimates
            from .models import CostEstimate
            estimates = CostEstimate.objects.filter(
                category=reminder.category,
                make__iexact=vehicle.make,
                year_start__lte=vehicle.year,
                year_end__gte=vehicle.year
            ).first()

            if estimates:
                reminder.suggested_cost = estimates.average_cost

            # Set status based on due date
            today = timezone.now().date()
            if reminder.due_date:
                days_until = (reminder.due_date - today).days
                if days_until < 0:
                    reminder.status = 'overdue'
                elif days_until <= 14:
                    reminder.status = 'due_soon'

            # Set status based on mileage
            if reminder.due_mileage and reminder.due_mileage <= vehicle.current_mileage:
                reminder.status = 'overdue'

            reminder.save()
            messages.success(request, 'Maintenance reminder created successfully!')
            return redirect('vehicle-detail', pk=vehicle.pk)
    else:
        form = MaintenanceReminderForm(vehicle=vehicle)

    return render(request, 'maintenance/reminder_form.html', {
        'form': form,
        'vehicle': vehicle,
        'title': 'Add Maintenance Reminder'
    })

@login_required
def reminder_update(request, pk):
    reminder = get_object_or_404(MaintenanceReminder, pk=pk, vehicle__user=request.user)
    vehicle = reminder.vehicle

    if request.method == 'POST':
        form = MaintenanceReminderForm(request.POST, instance=reminder, vehicle=vehicle)
        if form.is_valid():
            form.save()
            messages.success(request, 'Maintenance reminder updated successfully!')
            return redirect('reminder-list')
    else:
        form = MaintenanceReminderForm(instance=reminder, vehicle=vehicle)

    return render(request, 'maintenance/reminder_form.html', {
        'form': form,
        'vehicle': vehicle,
        'reminder': reminder,
        'title': 'Update Maintenance Reminder'
    })

@login_required
def reminder_delete(request, pk):
    reminder = get_object_or_404(MaintenanceReminder, pk=pk, vehicle__user=request.user)

    if request.method == 'POST':
        reminder.delete()
        messages.success(request, 'Maintenance reminder deleted successfully!')
        return redirect('reminder-list')

    return render(request, 'maintenance/reminder_confirm_delete.html', {
        'reminder': reminder
    })

@login_required
def reminder_complete(request, pk):
    reminder = get_object_or_404(MaintenanceReminder, pk=pk, vehicle__user=request.user)

    if request.method == 'POST':
        # Mark reminder as completed
        reminder.status = 'completed'
        reminder.last_service_date = timezone.now().date()
        reminder.last_service_mileage = reminder.vehicle.current_mileage
        reminder.save()

        # Pre-fill maintenance record form with reminder data
        initial_data = {
            'category': reminder.category,
            'service_date': timezone.now().date(),
            'mileage_at_service': reminder.vehicle.current_mileage,
        }

        if reminder.suggested_cost:
            initial_data['cost'] = reminder.suggested_cost

        # Redirect to maintenance record creation form
        messages.success(request, 'Reminder marked as completed. Add the maintenance details below.')
        return redirect('maintenance-create', vehicle_id=reminder.vehicle.id)

    return render(request, 'maintenance/reminder_complete.html', {
        'reminder': reminder
    })
