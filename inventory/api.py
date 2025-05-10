from rest_framework import viewsets, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .models import Device, DeviceType, MaintenanceRecord
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def dashboard_stats(request):
    """API endpoint for dashboard statistics"""
    
    # Get counts for different device statuses
    status_counts = list(Device.objects.values('status')
                        .annotate(count=Count('id'))
                        .order_by('status'))
    
    # Get counts for different device types
    type_counts = list(Device.objects.values('device_type__name')
                      .annotate(count=Count('id'))
                      .order_by('device_type__name'))
    
    # Get upcoming maintenance in the next 30 days
    today = timezone.now()
    thirty_days_later = today + timedelta(days=30)
    
    upcoming_maintenance = list(MaintenanceRecord.objects.filter(
        next_maintenance_date__gte=today,
        next_maintenance_date__lte=thirty_days_later
    ).values('device__name', 'next_maintenance_date', 'maintenance_type')
                               .order_by('next_maintenance_date'))
    
    # Get recent devices (added in the last 7 days)
    seven_days_ago = today - timedelta(days=7)
    recent_devices = list(Device.objects.filter(
        created_at__gte=seven_days_ago
    ).values('name', 'device_type__name', 'created_at')
                         .order_by('-created_at'))
    
    return Response({
        'status_counts': status_counts,
        'type_counts': type_counts,
        'upcoming_maintenance': upcoming_maintenance,
        'recent_devices': recent_devices,
        'total_devices': Device.objects.count(),
        'total_maintenance': MaintenanceRecord.objects.count(),
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def device_search(request):
    """API endpoint for searching devices"""
    query = request.query_params.get('q', '')
    
    if not query:
        return Response([])
    
    devices = Device.objects.filter(
        name__icontains=query
    ) | Device.objects.filter(
        serial_number__icontains=query
    ) | Device.objects.filter(
        model__icontains=query
    )
    
    results = list(devices.values('id', 'name', 'serial_number', 'device_type__name')[:10])
    
    return Response(results)
