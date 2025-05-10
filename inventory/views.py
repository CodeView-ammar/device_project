from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden, Http404
from django.db.models import Count, Max
from django.utils import timezone, translation
from django.contrib import messages
from django.conf import settings

from .models import Device, DeviceType, MaintenanceRecord
from .forms import DeviceForm, MaintenanceRecordForm, DeviceTypeForm,CheckpointForm
from .utils import generate_barcode_svg

import json
from datetime import timedelta


@login_required
def dashboard(request):
    """Display the main dashboard"""
    # Get counts for different device types
    device_counts = Device.objects.values('device_type__name').annotate(count=Count('id'))
    
    # Get counts for different device statuses
    status_counts = Device.objects.values('status').annotate(count=Count('id'))
    
    # Get upcoming maintenance
    upcoming_maintenance = MaintenanceRecord.objects.filter(
        next_maintenance_date__gt=timezone.now()
    ).order_by('next_maintenance_date')[:5]
    
    # Recent devices
    recent_devices = Device.objects.order_by('-created_at')[:5]
    
    # Devices needing attention (in maintenance or repair)
    attention_devices = Device.objects.filter(status__in=['maintenance', 'repair'])
    
    context = {
        'total_devices': Device.objects.count(),
        'active_devices': Device.objects.filter(status='active').count(),
        'maintenance_devices': Device.objects.filter(status='maintenance').count(),
        'repair_devices': Device.objects.filter(status='repair').count(),
        'retired_devices': Device.objects.filter(status='retired').count(),
        'device_counts': device_counts,
        'status_counts': status_counts,
        'upcoming_maintenance': upcoming_maintenance,
        'recent_devices': recent_devices,
        'attention_devices': attention_devices,
    }
    
    return render(request, 'dashboard.html', context)


@login_required
def device_list(request):
    """Display a list of all devices with filtering options"""
    devices = Device.objects.all()
    
    # Handle search query
    query = request.GET.get('q')
    if query:
        devices = devices.filter(
            name__icontains=query
        ) | devices.filter(
            serial_number__icontains=query
        ) | devices.filter(
            model__icontains=query
        )
    
    # Handle device type filter
    device_type = request.GET.get('device_type')
    if device_type and device_type != 'all':
        devices = devices.filter(device_type__id=device_type)
    
    # Handle status filter
    status = request.GET.get('status')
    if status and status != 'all':
        devices = devices.filter(status=status)
    
    # Get all device types for the filter dropdown
    device_types = DeviceType.objects.all()
    
    context = {
        'devices': devices,
        'device_types': device_types,
        'selected_type': device_type,
        'selected_status': status,
        'query': query,
    }
    
    return render(request, 'inventory/device_list.html', context)


@login_required
def device_detail(request, pk):
    """Display details for a specific device"""
    device = get_object_or_404(Device, pk=pk)
    maintenance_records = device.maintenance_records.order_by('-maintenance_date')
    
    context = {
        'device': device,
        'maintenance_records': maintenance_records,
    }
    
    return render(request, 'inventory/device_detail.html', context)


@login_required
def device_create(request):
    """Create a new device"""
    # Check if user has permission to add devices
    if not request.user.has_perm('inventory.add_device'):
        messages.error(request, 'You do not have permission to add devices.')
        return redirect('inventory:device_list')
        
    if request.method == 'POST':
        form = DeviceForm(request.POST)
        if form.is_valid():
            device = form.save(commit=False)
            device.created_by = request.user
            device.save()
            messages.success(request, f'Device "{device.name}" has been created.')
            return redirect('inventory:device_detail', pk=device.pk)
    else:
        form = DeviceForm()
    
    context = {
        'form': form,
        'title': 'Add New Device',
    }
    
    return render(request, 'inventory/device_form.html', context)


@login_required
def device_update(request, pk):
    """Update an existing device"""
    device = get_object_or_404(Device, pk=pk)
    
    # Check if user has permission to change devices
    if not request.user.has_perm('inventory.change_device'):
        messages.error(request, 'You do not have permission to edit devices.')
        return redirect('inventory:device_detail', pk=device.pk)
    
    if request.method == 'POST':
        form = DeviceForm(request.POST, instance=device)
        if form.is_valid():
            device = form.save()
            messages.success(request, f'Device "{device.name}" has been updated.')
            return redirect('inventory:device_detail', pk=device.pk)
    else:
        form = DeviceForm(instance=device)
    
    context = {
        'form': form,
        'device': device,
        'title': 'Edit Device',
    }
    
    return render(request, 'inventory/device_form.html', context)


@login_required
def device_delete(request, pk):
    """Delete a device"""
    device = get_object_or_404(Device, pk=pk)
    
    # Check if user has permission to delete devices
    if not request.user.has_perm('inventory.delete_device'):
        messages.error(request, 'You do not have permission to delete devices.')
        return redirect('inventory:device_detail', pk=device.pk)
    
    if request.method == 'POST':
        device_name = device.name
        device.delete()
        messages.success(request, f'Device "{device_name}" has been deleted.')
        return redirect('inventory:device_list')
    
    context = {
        'device': device,
    }
    
    return render(request, 'inventory/device_confirm_delete.html', context)

from django.urls import reverse
from urllib.parse import quote  # to safely encode the barcode in the URL

@login_required
def device_barcode(request, pk):
    """Generate and display barcode for a device"""
    device = get_object_or_404(Device, pk=pk)

    # تأكد من تحويل barcode إلى string قبل ترميزه
    encoded_barcode = quote(str(device.barcode))

    # إنشاء رابط الفحص باستخدام reverse
    scan_url = f"{request.scheme}://{request.get_host()}{reverse('inventory:scan_barcode', args=[encoded_barcode])}"

    # إنشاء الباركود بصيغة SVG
    barcode_svg = generate_barcode_svg(scan_url)

    context = {
        'device': device,
        'barcode_svg': barcode_svg,
    }

    return render(request, 'inventory/barcode.html', context)


@login_required
def maintenance_create(request, device_id):
    """Create a new maintenance record for a device"""
    device = get_object_or_404(Device, pk=device_id)
    
    # Check if user has permission to add maintenance records
    if not request.user.has_perm('inventory.add_maintenancerecord'):
        messages.error(request, 'You do not have permission to add maintenance records.')
        return redirect('inventory:device_detail', pk=device_id)
    
    if request.method == 'POST':
        form = MaintenanceRecordForm(request.POST)
        if form.is_valid():
            maintenance = form.save(commit=False)
            maintenance.device = device
            maintenance.created_by = request.user
            maintenance.save()
            
            # Update device status if needed
            if maintenance.maintenance_type in ['repair', 'routine']:
                device.status = 'active'
                device.save()
            
            messages.success(request, 'Maintenance record has been added.')
            return redirect('inventory:device_detail', pk=device.pk)
    else:
        form = MaintenanceRecordForm()
    
    context = {
        'form': form,
        'device': device,
        'title': 'Add Maintenance Record',
    }
    
    return render(request, 'inventory/maintenance_form.html', context)


@login_required
def maintenance_update(request, pk):
    """Update an existing maintenance record"""
    maintenance = get_object_or_404(MaintenanceRecord, pk=pk)
    
    # Check if user has permission to change maintenance records
    if not request.user.has_perm('inventory.change_maintenancerecord'):
        messages.error(request, 'You do not have permission to edit maintenance records.')
        return redirect('inventory:device_detail', pk=maintenance.device.pk)
    
    if request.method == 'POST':
        form = MaintenanceRecordForm(request.POST, instance=maintenance)
        if form.is_valid():
            maintenance = form.save()
            messages.success(request, 'Maintenance record has been updated.')
            return redirect('inventory:device_detail', pk=maintenance.device.pk)
    else:
        form = MaintenanceRecordForm(instance=maintenance)
    
    context = {
        'form': form,
        'maintenance': maintenance,
        'device': maintenance.device,
        'title': 'Edit Maintenance Record',
    }
    
    return render(request, 'inventory/maintenance_form.html', context)


@login_required
def maintenance_delete(request, pk):
    """Delete a maintenance record"""
    maintenance = get_object_or_404(MaintenanceRecord, pk=pk)
    device = maintenance.device
    
    # Check if user has permission to delete maintenance records
    if not request.user.has_perm('inventory.delete_maintenancerecord'):
        messages.error(request, 'You do not have permission to delete maintenance records.')
        return redirect('inventory:device_detail', pk=device.pk)
    
    if request.method == 'POST':
        maintenance.delete()
        messages.success(request, 'Maintenance record has been deleted.')
        return redirect('inventory:device_detail', pk=device.pk)
    
    context = {
        'maintenance': maintenance,
        'device': device,
    }
    
    return render(request, 'inventory/maintenance_confirm_delete.html', context)


@login_required
def device_type_list(request):
    """Display a list of all device types"""
    device_types = DeviceType.objects.all()
    
    context = {
        'device_types': device_types,
    }
    
    return render(request, 'inventory/device_type_list.html', context)


@login_required
def device_type_create(request):
    """Create a new device type"""
    # Check if user has permission to add device types
    if not request.user.has_perm('inventory.add_devicetype'):
        messages.error(request, 'You do not have permission to add device types.')
        return redirect('inventory:device_type_list')
        
    if request.method == 'POST':
        form = DeviceTypeForm(request.POST)
        if form.is_valid():
            device_type = form.save()
            messages.success(request, f'Device type "{device_type.name}" has been created.')
            return redirect('inventory:device_type_list')
    else:
        form = DeviceTypeForm()
    
    context = {
        'form': form,
        'title': 'Add Device Type',
    }
    
    return render(request, 'inventory/device_type_form.html', context)


@login_required
def device_type_update(request, pk):
    """Update an existing device type"""
    device_type = get_object_or_404(DeviceType, pk=pk)
    
    # Check if user has permission to change device types
    if not request.user.has_perm('inventory.change_devicetype'):
        messages.error(request, 'You do not have permission to edit device types.')
        return redirect('inventory:device_type_list')
    
    if request.method == 'POST':
        form = DeviceTypeForm(request.POST, instance=device_type)
        if form.is_valid():
            device_type = form.save()
            messages.success(request, f'Device type "{device_type.name}" has been updated.')
            return redirect('inventory:device_type_list')
    else:
        form = DeviceTypeForm(instance=device_type)
    
    context = {
        'form': form,
        'device_type': device_type,
        'title': 'Edit Device Type',
    }
    
    return render(request, 'inventory/device_type_form.html', context)


@login_required
def device_stats(request):
    """API endpoint for device statistics"""
    # Get device counts by type for pie chart
    type_data = list(Device.objects.values('device_type__name')
                     .annotate(count=Count('id'))
                     .order_by('-count'))
    
    # Get device counts by status for bar chart
    status_data = list(Device.objects.values('status')
                       .annotate(count=Count('id'))
                       .order_by('status'))
    
    # Get device acquisition trend by month for line chart
    current_date = timezone.now().date()
    six_months_ago = current_date - timedelta(days=180)
    
    devices_by_month = Device.objects.filter(
        acquisition_date__gte=six_months_ago
    ).values('acquisition_date__year', 'acquisition_date__month').annotate(
        count=Count('id')
    ).order_by('acquisition_date__year', 'acquisition_date__month')
    
    month_labels = []
    month_data = []
    
    for item in devices_by_month:
        month_labels.append(f"{item['acquisition_date__year']}-{item['acquisition_date__month']}")
        month_data.append(item['count'])
    
    data = {
        'type_labels': [item['device_type__name'] for item in type_data],
        'type_data': [item['count'] for item in type_data],
        'status_labels': [item['status'] for item in status_data],
        'status_data': [item['count'] for item in status_data],
        'month_labels': month_labels,
        'month_data': month_data,
    }
    
    return JsonResponse(data)


@login_required
def maintenance_stats(request):
    """API endpoint for maintenance statistics"""
    # Get maintenance counts by type for pie chart
    type_data = list(MaintenanceRecord.objects.values('maintenance_type')
                     .annotate(count=Count('id'))
                     .order_by('-count'))
    
    # Get maintenance trend by month for line chart
    current_date = timezone.now().date()
    six_months_ago = current_date - timedelta(days=180)
    
    maintenance_by_month = MaintenanceRecord.objects.filter(
        maintenance_date__gte=six_months_ago
    ).values('maintenance_date__year', 'maintenance_date__month').annotate(
        count=Count('id')
    ).order_by('maintenance_date__year', 'maintenance_date__month')
    
    month_labels = []
    month_data = []
    
    for item in maintenance_by_month:
        month_labels.append(f"{item['maintenance_date__year']}-{item['maintenance_date__month']}")
        month_data.append(item['count'])
    
    data = {
        'type_labels': [item['maintenance_type'] for item in type_data],
        'type_data': [item['count'] for item in type_data],
        'month_labels': month_labels,
        'month_data': month_data,
    }
    
    return JsonResponse(data)


def scan_barcode(request, barcode):
    """
    Handle barcode scanning functionality
    When a barcode is scanned, display device details, show maintenance history,
    and provide an option to add a new maintenance record.
    This view can be accessed without login to support public barcode scanning.
    """
    try:
        device = get_object_or_404(Device, barcode=barcode)
        
        # Get maintenance records for this device, ordered by most recent first
        maintenance_records = device.maintenance_records.order_by('-maintenance_date')
        # Get the last maintenance record
        last_maintenance = maintenance_records.first()
        
        # Get maintenance records for this device, ordered by most recent first
        next_maintenance_date = device.get_next_maintenance_date()
        # Get the last maintenance record
        next_maintenance = next_maintenance_date
        

        # If the user submitted a quick maintenance form
        if request.method == 'POST':
            # Check if user is logged in
            if not request.user.is_authenticated:
                return redirect('accounts:login')
                
            # Check if user has permission to add maintenance records
            if not request.user.has_perm('inventory.add_maintenancerecord'):
                messages.error(request, 'You do not have permission to add maintenance records.')
                return redirect('inventory:scan_barcode', barcode=barcode)
                
            form = MaintenanceRecordForm(request.POST)
            if form.is_valid():
                maintenance = form.save(commit=False)
                maintenance.device = device
                maintenance.created_by = request.user
                maintenance.save()
                
                # Update device status if needed
                if maintenance.maintenance_type in ['repair', 'routine']:
                    device.status = 'active'
                    device.save()
                
                messages.success(request, 'تم إضافة سجل الصيانة بنجاح.')
                return redirect('inventory:scan_barcode', barcode=barcode)
        else:
            form = MaintenanceRecordForm()
            checkpoint=CheckpointForm()
        
        # Check if user has permission to add maintenance records (for UI display)
        can_add_maintenance = request.user.is_authenticated and request.user.has_perm('inventory.add_maintenancerecord')
        
        context = {
            'device': device,
            'maintenance_records': maintenance_records[:5],  # Show only the 5 most recent
            'last_maintenance': last_maintenance,
            'next_maintenance': next_maintenance,
            'form': form,
            'is_authenticated': request.user.is_authenticated,
            'can_add_maintenance': can_add_maintenance
        }
        
        return render(request, 'inventory/scan_result.html', context)
        
    except Http404:
        # Device not found
        context = {
            'barcode': barcode,
            'error': 'لم يتم العثور على جهاز بهذا الباركود'
        }
        
        return render(request, 'inventory/scan_error.html', context)


def change_language(request):
    """
    Change the current language.
    This view handles switching between available languages.
    """
    lang_code = request.GET.get('lang', None)
    next_url = request.GET.get('next', '/')

    if lang_code and lang_code in [code for code, name in settings.LANGUAGES]:
        translation.activate(lang_code)
        response = redirect(next_url)
        response.set_cookie(settings.LANGUAGE_COOKIE_NAME, lang_code)
        return response
    
    return redirect(next_url)
