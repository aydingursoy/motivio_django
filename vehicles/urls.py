from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('dashboard/', views.dashboard, name='dashboard'),

    # Vehicle management
    path('vehicles/', views.vehicle_list, name='vehicle-list'),
    path('vehicles/new/', views.vehicle_create, name='vehicle-create'),
    path('vehicles/<int:pk>/', views.vehicle_detail, name='vehicle-detail'),
    path('vehicles/<int:pk>/update/', views.vehicle_update, name='vehicle-update'),
    path('vehicles/<int:pk>/delete/', views.vehicle_delete, name='vehicle-delete'),

    # Mileage tracking
    path('vehicles/<int:vehicle_id>/mileage/add/', views.mileage_record_create, name='mileage-create'),
    path('mileage/<int:pk>/update/', views.mileage_record_update, name='mileage-update'),
    path('mileage/<int:pk>/delete/', views.mileage_record_delete, name='mileage-delete'),
]
