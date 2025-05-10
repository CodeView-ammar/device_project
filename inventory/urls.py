from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    # Dashboard - Moved to project-level urls.py
    # path('', views.dashboard, name='dashboard'),
    
    # Device management
    path('devices/', views.device_list, name='device_list'),
    path('devices/add/', views.device_create, name='device_create'),
    path('devices/<int:pk>/', views.device_detail, name='device_detail'),
    path('devices/<int:pk>/edit/', views.device_update, name='device_update'),
    path('devices/<int:pk>/delete/', views.device_delete, name='device_delete'),
    path('devices/<int:pk>/barcode/', views.device_barcode, name='device_barcode'),
    
    # Barcode scanning
    path('scan/<uuid:barcode>/', views.scan_barcode, name='scan_barcode'),
    
    # Maintenance records
    path('devices/<int:device_id>/maintenance/add/', views.maintenance_create, name='maintenance_create'),
    path('maintenance/<int:pk>/edit/', views.maintenance_update, name='maintenance_update'),
    path('maintenance/<int:pk>/delete/', views.maintenance_delete, name='maintenance_delete'),
    
    # Device types
    path('device-types/', views.device_type_list, name='device_type_list'),
    path('device-types/add/', views.device_type_create, name='device_type_create'),
    path('device-types/<int:pk>/edit/', views.device_type_update, name='device_type_update'),
    
    # API endpoints
    path('api/device-stats/', views.device_stats, name='device_stats'),
    path('api/maintenance-stats/', views.maintenance_stats, name='maintenance_stats'),
]
