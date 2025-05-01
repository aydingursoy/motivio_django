from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'vehicles', views.VehicleViewSet, basename='api-vehicle')
router.register(r'maintenance-records', views.MaintenanceRecordViewSet, basename='maintenance-record')
router.register(r'maintenance-reminders', views.MaintenanceReminderViewSet, basename='maintenance-reminder')
router.register(r'cost-estimates', views.CostEstimateViewSet, basename='cost-estimates')

urlpatterns = [
    path('', include(router.urls)),
    path('vehicle-stats/', views.vehicle_stats, name='vehicle-stats'),
    path('maintenance-stats/', views.maintenance_stats, name='maintenance-stats'),
]
