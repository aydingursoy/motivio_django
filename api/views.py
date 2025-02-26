from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from vehicles.models import Vehicle, MileageRecord
from maintenance.models import MaintenanceRecord, MaintenanceReminder, CostEstimate, MaintenanceCategory
from .serializers import (
    VehicleSerializer, MaintenanceRecordSerializer,
    MaintenanceReminderSerializer, CostEstimateSerializer
)
from django.db.models import Sum, Avg, Count
from django.utils import timezone
import datetime

class VehicleViewSet(viewsets.ModelViewSet):
    serializer_class = VehicleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Vehicle.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class MaintenanceRecordViewSet(viewsets.ModelViewSet):
    serializer_class = MaintenanceRecordSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return MaintenanceRecord.objects.filter(vehicle__user=self.request.user)

class MaintenanceReminderViewSet(viewsets.ModelViewSet):
    serializer_class = MaintenanceReminderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return MaintenanceReminder.objects.filter(vehicle__user=self.request.user)

class CostEstimateViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CostEstimateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Get all cost estimates - this data is shared among all users
        return CostEstimate.objects.all()

    def list(self, request):
        # Optional filtering
        make = request.query_params.get('make', None)
        model = request.query_params.get('model', None)
        year = request.query_params.get('year', None)
        category_id = request.query_params.get('category', None)

        queryset = self.get_queryset()

        if make:
            queryset = queryset.filter(make__iexact=make)
        if model:
            queryset = queryset.filter(model__iexact=model)
        if year:
            queryset = queryset.filter(year_start__lte=year, year_end__gte=year)
        if category_id:
            queryset = queryset.filter(category_id=category_id)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def vehicle_stats(request):
    """Get statistics about the user's vehicles"""
    vehicles = Vehicle.objects.filter(user=request.user)

    # Get basic counts
    vehicle_count = vehicles.count()
    total_maintenance_records = MaintenanceRecord.objects.filter(vehicle__in=vehicles).count()

    # Get total spending by vehicle
    vehicle_spending = []
    for vehicle in vehicles:
        records = MaintenanceRecord.objects.filter(vehicle=vehicle)
        total_spent = records.aggregate(Sum('cost'))['cost__sum'] or 0
        record_count = records.count()

        vehicle_spending.append({
            'id': vehicle.id,
            'name': str(vehicle),
            'total_spent': total_spent,
            'record_count': record_count,
            'avg_cost_per_record': total_spent / record_count if record_count > 0 else 0
        })

    # Get upcoming reminders
    upcoming_reminders = MaintenanceReminder.objects.filter(
        vehicle__user=request.user,
        status__in=['pending', 'due_soon', 'overdue']
    ).order_by('due_date')[:5]

    upcoming = []
    for reminder in upcoming_reminders:
        upcoming.append({
            'id': reminder.id,
            'vehicle': str(reminder.vehicle),
            'category': reminder.category.name,
            'due_date': reminder.due_date,
            'due_mileage': reminder.due_mileage,
            'status': reminder.status
        })

    return Response({
        'vehicle_count': vehicle_count,
        'total_maintenance_records': total_maintenance_records,
        'vehicle_spending': vehicle_spending,
        'upcoming_reminders': upcoming
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def maintenance_stats(request):
    """Get maintenance statistics for the user's vehicles"""
    # Optional filtering by vehicle
    vehicle_id = request.query_params.get('vehicle', None)

    # Get all user's maintenance records
    records = MaintenanceRecord.objects.filter(vehicle__user=request.user)

    if vehicle_id:
        records = records.filter(vehicle_id=vehicle_id)

    # Get total and average costs
    cost_stats = records.aggregate(
        total_cost=Sum('cost'),
        avg_cost=Avg('cost'),
        record_count=Count('id')
    )

    # Get spending by category
    categories = MaintenanceCategory.objects.filter(
        maintenancerecord__in=records
    ).distinct()

    category_spending = []
    for category in categories:
        category_records = records.filter(category=category)
        total = category_records.aggregate(Sum('cost'))['cost__sum'] or 0
        avg = category_records.aggregate(Avg('cost'))['cost__avg'] or 0
        count = category_records.count()

        category_spending.append({
            'id': category.id,
            'name': category.name,
            'total_spent': total,
            'avg_cost': avg,
            'record_count': count
        })

    # Get spending over time
    now = timezone.now()
    last_year = now - datetime.timedelta(days=365)

    monthly_spending = records.filter(
        service_date__gte=last_year
    ).extra({
        'month': "EXTRACT(month FROM service_date)",
        'year': "EXTRACT(year FROM service_date)"
    }).values('month', 'year').annotate(
        total=Sum('cost')
    ).order_by('year', 'month')

    # Format for the response
    spending_by_month = []
    for item in monthly_spending:
        month_name = datetime.date(int(item['year']), int(item['month']), 1).strftime('%b %Y')
        spending_by_month.append({
            'month': month_name,
            'total': item['total']
        })

    # Compare actual costs to estimates
    cost_comparisons = []
    records_with_estimates = records.exclude(estimated_cost=None)

    for record in records_with_estimates:
        diff_amount = record.cost - record.estimated_cost
        diff_percent = (diff_amount / record.estimated_cost * 100) if record.estimated_cost else 0

        cost_comparisons.append({
            'id': record.id,
            'vehicle': str(record.vehicle),
            'category': record.category.name,
            'service_date': record.service_date,
            'estimated_cost': record.estimated_cost,
            'actual_cost': record.cost,
            'difference': diff_amount,
            'diff_percent': diff_percent
        })

    return Response({
        'cost_stats': cost_stats,
        'category_spending': category_spending,
        'spending_by_month': spending_by_month,
        'cost_comparisons': cost_comparisons
    })
