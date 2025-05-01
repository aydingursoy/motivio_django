from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Vehicle, MileageRecord
from .forms import VehicleForm, MileageRecordForm
from maintenance.models import MaintenanceRecord, MaintenanceReminder
from django.db.models import Count, Sum, Avg
from django.utils import timezone
import datetime

def home(request):
    return render(request, 'vehicles/home.html')

def about(request):
    return render(request, 'vehicles/about.html')

@login_required
def dashboard(request):
    vehicles = Vehicle.objects.filter(user=request.user)

    # Get upcoming maintenance reminders
    reminders = MaintenanceReminder.objects.filter(
        vehicle__user=request.user,
        status__in=['pending', 'due_soon', 'overdue']
    ).order_by('due_date')[:5]

    # Get recent maintenance records
    recent_maintenance = MaintenanceRecord.objects.filter(
        vehicle__user=request.user
    ).order_by('-service_date')[:5]

    # Calculate total spend on maintenance
    maintenance_stats = MaintenanceRecord.objects.filter(
        vehicle__user=request.user
    ).aggregate(
        total_spent=Sum('cost'),
        avg_cost=Avg('cost'),
        record_count=Count('id')
    )

    context = {
        'vehicles': vehicles,
        'reminders': reminders,
        'recent_maintenance': recent_maintenance,
        'maintenance_stats': maintenance_stats,
    }
    return render(request, 'vehicles/dashboard.html', context)

@login_required
def vehicle_list(request):
    vehicles = Vehicle.objects.filter(user=request.user)
    return render(request, 'vehicles/vehicle_list.html', {'vehicles': vehicles})

@login_required
def vehicle_detail(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk, user=request.user)

    # Get maintenance records for this vehicle
    maintenance_records = MaintenanceRecord.objects.filter(vehicle=vehicle).order_by('-service_date')

    # Get maintenance reminders for this vehicle
    reminders = MaintenanceReminder.objects.filter(vehicle=vehicle).order_by('due_date')

    # Get mileage history
    mileage_records = MileageRecord.objects.filter(vehicle=vehicle).order_by('-date_recorded')

    # Check for upcoming or overdue maintenance
    today = timezone.now().date()
    for reminder in reminders:
        if reminder.due_date:
            days_until = (reminder.due_date - today).days
            if days_until < 0:
                reminder.status = 'overdue'
                reminder.save()
            elif days_until <= 14:
                reminder.status = 'due_soon'
                reminder.save()

        if reminder.due_mileage and reminder.due_mileage <= vehicle.current_mileage:
            reminder.status = 'overdue'
            reminder.save()

    context = {
        'vehicle': vehicle,
        'maintenance_records': maintenance_records,
        'reminders': reminders,
        'mileage_records': mileage_records,
    }
    return render(request, 'vehicles/vehicle_detail.html', context)

@login_required
def vehicle_create(request):
    if request.method == 'POST':
        form = VehicleForm(request.POST, request.FILES)
        if form.is_valid():
            vehicle = form.save(commit=False)
            vehicle.user = request.user
            vehicle.save()
            messages.success(request, f'Vehicle added successfully!')
            return redirect('vehicle-detail', pk=vehicle.pk)
    else:
        form = VehicleForm()

    return render(request, 'vehicles/vehicle_form.html', {'form': form, 'title': 'Add Vehicle'})

@login_required
def vehicle_update(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk, user=request.user)

    if request.method == 'POST':
        form = VehicleForm(request.POST, request.FILES, instance=vehicle)
        if form.is_valid():
            form.save()
            messages.success(request, f'Vehicle updated successfully!')
            return redirect('vehicle-detail', pk=vehicle.pk)
    else:
        form = VehicleForm(instance=vehicle)

    return render(request, 'vehicles/vehicle_form.html', {
        'form': form,
        'title': 'Update Vehicle',
        'vehicle': vehicle
    })

@login_required
def vehicle_delete(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk, user=request.user)

    if request.method == 'POST':
        vehicle.delete()
        messages.success(request, f'Vehicle deleted successfully!')
        return redirect('vehicle-list')

    return render(request, 'vehicles/vehicle_confirm_delete.html', {'vehicle': vehicle})

@login_required
def mileage_record_create(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, pk=vehicle_id, user=request.user)

    if request.method == 'POST':
        form = MileageRecordForm(request.POST, vehicle=vehicle)
        if form.is_valid():
            mileage_record = form.save(commit=False)
            mileage_record.vehicle = vehicle
            mileage_record.save()

            # Update vehicle's current mileage if new record has higher mileage
            if mileage_record.mileage > vehicle.current_mileage:
                vehicle.current_mileage = mileage_record.mileage
                vehicle.save()

            messages.success(request, f'Mileage record added successfully!')
            return redirect('vehicle-detail', pk=vehicle.pk)
    else:
        form = MileageRecordForm(
            vehicle=vehicle,
            initial={'mileage': vehicle.current_mileage, 'date_recorded': datetime.date.today()}
        )

    return render(request, 'vehicles/mileage_form.html', {
        'form': form,
        'vehicle': vehicle,
        'title': 'Add Mileage Record'
    })

@login_required
def mileage_record_update(request, pk):
    mileage_record = get_object_or_404(MileageRecord, pk=pk, vehicle__user=request.user)
    vehicle = mileage_record.vehicle

    if request.method == 'POST':
        form = MileageRecordForm(request.POST, instance=mileage_record, vehicle=vehicle)
        if form.is_valid():
            form.save()

            # Update vehicle's current mileage if updated record has highest mileage
            highest_mileage = MileageRecord.objects.filter(vehicle=vehicle).order_by('-mileage').first().mileage
            if highest_mileage > vehicle.current_mileage:
                vehicle.current_mileage = highest_mileage
                vehicle.save()

            messages.success(request, f'Mileage record updated successfully!')
            return redirect('vehicle-detail', pk=vehicle.pk)
    else:
        form = MileageRecordForm(instance=mileage_record, vehicle=vehicle)

    return render(request, 'vehicles/mileage_form.html', {
        'form': form,
        'vehicle': vehicle,
        'title': 'Update Mileage Record'
    })

@login_required
def mileage_record_delete(request, pk):
    mileage_record = get_object_or_404(MileageRecord, pk=pk, vehicle__user=request.user)
    vehicle = mileage_record.vehicle

    if request.method == 'POST':
        mileage_record.delete()

        # Update vehicle's current mileage if we deleted the highest mileage record
        highest_mileage_record = MileageRecord.objects.filter(vehicle=vehicle).order_by('-mileage').first()
        if highest_mileage_record and highest_mileage_record.mileage > vehicle.current_mileage:
            vehicle.current_mileage = highest_mileage_record.mileage
            vehicle.save()

        messages.success(request, f'Mileage record deleted successfully!')
        return redirect('vehicle-detail', pk=vehicle.pk)

    return render(request, 'vehicles/mileage_confirm_delete.html', {
        'mileage_record': mileage_record,
        'vehicle': vehicle
    })
