from django.urls import path
from . import views

urlpatterns = [
    # Maintenance records
    path('', views.maintenance_list, name='maintenance-list'),
    path('vehicle/<int:vehicle_id>/add/', views.maintenance_create, name='maintenance-create'),
    path('<int:pk>/', views.maintenance_detail, name='maintenance-detail'),
    path('<int:pk>/update/', views.maintenance_update, name='maintenance-update'),
    path('<int:pk>/delete/', views.maintenance_delete, name='maintenance-delete'),

    # Maintenance reminders
    path('reminders/', views.reminder_list, name='reminder-list'),
    path('reminders/vehicle/<int:vehicle_id>/add/', views.reminder_create, name='reminder-create'),
    path('reminders/<int:pk>/update/', views.reminder_update, name='reminder-update'),
    path('reminders/<int:pk>/delete/', views.reminder_delete, name='reminder-delete'),
    path('reminders/<int:pk>/complete/', views.reminder_complete, name='reminder-complete'),
]
