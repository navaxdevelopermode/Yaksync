import json
from datetime import timedelta
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.views import View
from django.views.generic import DetailView, ListView

from apps.animals.models import Animal
from apps.devices.models import Device
from .models import SensorReading


class MockAnimal:
    pk = 999
    animal_id = 'Yak 834'
    name = 'Gaptamu (Demo)'
    species = 'Yak'
    breed = 'Yak'
    age = 5
    gender = 'female'
    weight = 225.0
    health_status = 'healthy'
    reproductive_status = 'cycling'
    vagina_temperature = 37.38


class MockDevice:
    pk = 999
    device_id = 'DEV-834'
    name = 'Yak 834 Collar Sensor'
    device_type = 'sensor'
    installation_location = 'Collar'
    status = 'active'
    battery_level = 95
    assigned_animal = None
    last_communication = None


def get_animal_telemetry_context(animal):
    is_mock = isinstance(animal, MockAnimal)
    
    device = None
    if not is_mock:
        device = Device.objects.filter(assigned_animal=animal).first()
        if not device and animal.animal_id == 'Yak 834':
            device = Device.objects.filter(device_id='DEV-834').first()
            if device:
                device.assigned_animal = animal
                device.save()
            else:
                device = Device.objects.create(
                    device_id='DEV-834',
                    name='Yak 834 Collar Sensor',
                    device_type='sensor',
                    installation_location='Collar',
                    status='active',
                    battery_level=95,
                    assigned_animal=animal
                )
    else:
        device = MockDevice()
        device.assigned_animal = animal

    # Check for real readings
    real_readings = SensorReading.objects.filter(animal=animal).order_by('-timestamp')
    has_real_readings = real_readings.exists()
    
    if has_real_readings:
        readings_qs = real_readings[:5]
        
        latest_reading = readings_qs[0] if readings_qs else None
        
        current_temp_val = float(latest_reading.temperature) if latest_reading else None
        current_move_val = int(latest_reading.movement) if latest_reading else None
        
        last_updated_time = latest_reading.timestamp if latest_reading else timezone.now()
        
        # Calculate time ago
        diff = timezone.now() - last_updated_time
        if diff < timedelta(minutes=1):
            last_updated_str = "Just now"
        elif diff < timedelta(hours=1):
            mins = int(diff.total_seconds() / 60)
            last_updated_str = f"{mins} minute{'s' if mins != 1 else ''} ago"
        elif diff < timedelta(days=1):
            hours = int(diff.total_seconds() / 3600)
            last_updated_str = f"{hours} hour{'s' if hours != 1 else ''} ago"
        else:
            last_updated_str = last_updated_time.strftime('%b %d, %I:%M %p')
            
        # Determine device online status (60 seconds threshold)
        device_online = False
        if device and device.status == 'active':
            if device.last_communication and timezone.now() - device.last_communication < timedelta(seconds=60):
                device_online = True
            elif last_updated_time and timezone.now() - last_updated_time < timedelta(seconds=60):
                device_online = True
                
        readings_list = list(reversed(readings_qs))
        
        temp_chart_data = [{'timestamp': r.timestamp.strftime('%H:%M'), 'value': float(r.temperature)} for r in readings_list]
        move_chart_data = [{'timestamp': r.timestamp.strftime('%H:%M'), 'value': float(r.movement)} for r in readings_list]
        
        temp_values = [float(r.temperature) for r in readings_list]
        move_values = [float(r.movement) for r in readings_list]
    else:
        # Default/Demo data
        current_temp_val = 38.2
        current_move_val = 1400
        
        last_updated_time = timezone.now() - timedelta(minutes=2)
        last_updated_str = "2 minutes ago"
        device_online = True
        
        demo_temps = [38.1, 38.3, 38.2, 38.4, 38.1]
        demo_moves = [1200, 1500, 1100, 1300, 1400]
        
        base_time = timezone.now()
        temp_chart_data = []
        move_chart_data = []
        for i in range(5):
            t = base_time - timedelta(minutes=(5 - i) * 10)
            temp_chart_data.append({'timestamp': t.strftime('%H:%M'), 'value': demo_temps[i]})
            move_chart_data.append({'timestamp': t.strftime('%H:%M'), 'value': demo_moves[i]})
            
        temp_values = demo_temps
        move_values = demo_moves
        
    # Analyze trends
    temp_trend = "Stable"
    temp_trend_class = "success"
    if len(temp_values) >= 2:
        out_of_range = any(val < 37.5 or val > 39.5 for val in temp_values)
        sudden_spike = False
        for i in range(len(temp_values) - 1):
            if abs(temp_values[i+1] - temp_values[i]) > 0.5:
                sudden_spike = True
                break
        if out_of_range or sudden_spike:
            temp_trend = "Unstable"
            temp_trend_class = "danger"
            
    move_trend = "Normal Activity"
    move_trend_class = "success"
    if len(move_values) >= 2:
        out_of_range = any(val < 100 or val > 10000 for val in move_values)
        sudden_change = False
        for i in range(len(move_values) - 1):
            if abs(move_values[i+1] - move_values[i]) > 4000:
                sudden_change = True
                break
        if out_of_range or sudden_change:
            move_trend = "Abnormal Activity"
            move_trend_class = "danger"
            
    return {
        'device': device,
        'has_real_readings': has_real_readings,
        'current_temp': current_temp_val,
        'current_move': current_move_val,
        'last_updated_str': last_updated_str,
        'last_updated_time': last_updated_time,
        'device_online': device_online,
        'temp_chart_data': temp_chart_data,
        'move_chart_data': move_chart_data,
        'temp_values': temp_values,
        'move_values': move_values,
        'temp_trend': temp_trend,
        'temp_trend_class': temp_trend_class,
        'move_trend': move_trend,
        'move_trend_class': move_trend_class,
    }


class SensorReadingListView(LoginRequiredMixin, ListView):
    """Display sensor readings with search, filters, and pagination"""
    model = SensorReading
    template_name = 'monitoring/sensor_reading_list.html'
    context_object_name = 'readings'
    paginate_by = 10
    login_url = '/auth/login/'

    def get_queryset(self):
        queryset = SensorReading.objects.select_related('animal', 'device').all()

        search_query = self.request.GET.get('search', '').strip()
        if search_query:
            queryset = queryset.filter(
                Q(animal__animal_id__icontains=search_query) |
                Q(animal__name__icontains=search_query) |
                Q(device__device_id__icontains=search_query) |
                Q(device__name__icontains=search_query)
            )

        animal_id = self.request.GET.get('animal', '').strip()
        if animal_id:
            if animal_id.isdigit():
                queryset = queryset.filter(animal_id=animal_id)
            else:
                messages.error(self.request, 'Invalid animal filter selected.')
                queryset = queryset.none()

        device_id = self.request.GET.get('device', '').strip()
        if device_id:
            if device_id.isdigit():
                queryset = queryset.filter(device_id=device_id)
            else:
                messages.error(self.request, 'Invalid device filter selected.')
                queryset = queryset.none()

        start_date = self.request.GET.get('start_date', '').strip()
        end_date = self.request.GET.get('end_date', '').strip()
        parsed_start_date = parse_date(start_date) if start_date else None
        parsed_end_date = parse_date(end_date) if end_date else None

        if start_date and parsed_start_date is None:
            messages.error(self.request, 'Invalid start date. Please use a valid date.')
            queryset = queryset.none()
        elif end_date and parsed_end_date is None:
            messages.error(self.request, 'Invalid end date. Please use a valid date.')
            queryset = queryset.none()
        elif parsed_start_date and parsed_end_date and parsed_start_date > parsed_end_date:
            messages.error(self.request, 'Start date cannot be later than end date.')
            queryset = queryset.none()
        else:
            if parsed_start_date:
                queryset = queryset.filter(timestamp__date__gte=parsed_start_date)
            if parsed_end_date:
                queryset = queryset.filter(timestamp__date__lte=parsed_end_date)

        abnormal_only = self.request.GET.get('abnormal_only') == 'on'
        if abnormal_only:
            queryset = queryset.filter(is_abnormal=True)

        return queryset.order_by('-timestamp')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query_params = self.request.GET.copy()
        query_params.pop('page', None)

        context['search_query'] = self.request.GET.get('search', '')
        context['selected_animal'] = self.request.GET.get('animal', '')
        context['selected_device'] = self.request.GET.get('device', '')
        context['selected_start_date'] = self.request.GET.get('start_date', '')
        context['selected_end_date'] = self.request.GET.get('end_date', '')
        context['abnormal_only'] = self.request.GET.get('abnormal_only') == 'on'
        context['query_params'] = query_params.urlencode()
        context['animals'] = Animal.objects.order_by('animal_id')
        context['devices'] = Device.objects.order_by('device_id')
        
        # Add context for Yak 834 card
        yak = Animal.objects.filter(animal_id='Yak 834').first()
        if not yak:
            first_animal = Animal.objects.first()
            if first_animal:
                yak = first_animal
            else:
                yak = MockAnimal()
        
        yak_ctx = get_animal_telemetry_context(yak)
        context['yak_834'] = yak
        context['yak_834_device'] = yak_ctx['device']
        context['yak_834_temp'] = yak_ctx['current_temp']
        context['yak_834_move'] = yak_ctx['current_move']
        context['yak_834_last_updated'] = yak_ctx['last_updated_str']
        context['yak_834_online'] = yak_ctx['device_online']
        context['yak_834_has_real'] = yak_ctx['has_real_readings']
        
        return context


class SensorReadingDetailView(LoginRequiredMixin, DetailView):
    """Display detailed sensor reading information and recent related history"""
    model = SensorReading
    template_name = 'monitoring/sensor_reading_detail.html'
    context_object_name = 'reading'
    login_url = '/auth/login/'

    def get_queryset(self):
        return SensorReading.objects.select_related('animal', 'device')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['related_history'] = (
            SensorReading.objects.select_related('animal', 'device')
            .filter(animal=self.object.animal)
            .exclude(pk=self.object.pk)
            .order_by('-timestamp')[:10]
        )
        return context


class YakMonitoringDetailView(LoginRequiredMixin, DetailView):
    """Display detailed physiological monitoring metrics and graphs for a specific yak"""
    model = Animal
    template_name = 'monitoring/yak_detail.html'
    context_object_name = 'animal'
    login_url = '/auth/login/'

    def get_object(self, queryset=None):
        identifier = self.kwargs.get('animal_id')
        if identifier.isdigit():
            animal = Animal.objects.filter(pk=identifier).first()
            if animal:
                return animal
            animal = Animal.objects.filter(animal_id=f"Yak {identifier}").first()
            if animal:
                return animal
        
        animal = Animal.objects.filter(animal_id=identifier).first()
        if animal:
            return animal

        yak_834 = Animal.objects.filter(animal_id='Yak 834').first()
        if yak_834:
            return yak_834

        first_animal = Animal.objects.first()
        if first_animal:
            return first_animal

        return MockAnimal()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        animal = self.get_object()
        
        # Calculate context variables using the helper
        telemetry_ctx = get_animal_telemetry_context(animal)
        context.update(telemetry_ctx)
        
        # Serialize graph data for Chart.js
        context['temp_chart_json'] = json.dumps(telemetry_ctx['temp_chart_data'])
        context['move_chart_json'] = json.dumps(telemetry_ctx['move_chart_data'])
        
        return context


from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.conf import settings

@method_decorator(csrf_exempt, name='dispatch')
class SensorDataAPIView(View):
    """Secure API endpoint for ESP32 IoT devices to post physiological sensor readings"""
    
    def post(self, request, *args, **kwargs):
        # 1. API Key Authentication
        api_key = request.headers.get('X-API-Key')
        if not api_key:
            auth_header = request.headers.get('Authorization')
            if auth_header and auth_header.startswith('Bearer '):
                api_key = auth_header.split(' ', 1)[1]
                
        expected_key = getattr(settings, 'IOT_API_KEY', 'yaksync-iot-secure-token-2026')
        if not api_key or api_key != expected_key:
            return JsonResponse({'error': 'Unauthorized'}, status=401)
            
        # 2. Parse request JSON payload
        try:
            payload = json.loads(request.body)
        except (json.JSONDecodeError, TypeError):
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
            
        device_id = payload.get('device_id')
        yak_id = payload.get('yak_id')
        temperature = payload.get('temperature')
        movement = payload.get('movement')
        
        # Validation
        if not all([device_id, yak_id]) or temperature is None or movement is None:
            return JsonResponse({'error': 'Missing required fields'}, status=400)
            
        try:
            temp_val = float(temperature)
            move_val = float(movement)
        except ValueError:
            return JsonResponse({'error': 'Invalid reading values'}, status=400)
            
        # 3. Identify registered Device
        device = Device.objects.filter(device_id=device_id).first()
        if not device:
            # DO NOT automatically create unknown devices - return 404
            return JsonResponse({'error': f'Device {device_id} is not registered'}, status=404)
            
        # 4. Identify Yak 834 / animal
        # Try matching by animal_id = yak_id
        yak = Animal.objects.filter(animal_id=yak_id).first()
        if not yak:
            # Try matching by animal_id = "Yak " + yak_id
            yak = Animal.objects.filter(animal_id=f"Yak {yak_id}").first()
        if not yak and str(yak_id).isdigit():
            # In test suite or normal DB, the user might pass PK as integer/digit
            yak = Animal.objects.filter(pk=yak_id).first()
            
        if not yak:
            return JsonResponse({'error': f'Animal {yak_id} not found'}, status=404)
            
        # Ensure device is assigned to this animal
        if device.assigned_animal != yak:
            device.assigned_animal = yak
            device.save()
            
        # 5. Create SensorReading (temperature and movement together in one record)
        SensorReading.objects.create(
            animal=yak,
            device=device,
            temperature=temp_val,
            movement=move_val
        )
        
        # 6. Update device last_communication timestamp
        device.last_communication = timezone.now()
        device.save()
        
        return JsonResponse({'status': 'success'}, status=201)


class HerdTelemetryAPIView(LoginRequiredMixin, View):
    """API endpoint returning latest telemetry for the herd"""
    login_url = '/auth/login/'

    def get(self, request):
        readings = SensorReading.objects.select_related('animal').order_by('-timestamp')[:30]
        
        temp_data = [{
            'timestamp': r.timestamp.strftime('%H:%M'),
            'value': float(r.temperature),
            'animal_id': r.animal.animal_id,
        } for r in reversed(readings)]
        
        move_data = [{
            'timestamp': r.timestamp.strftime('%H:%M'),
            'value': float(r.movement),
            'animal_id': r.animal.animal_id,
        } for r in reversed(readings)]
        
        return JsonResponse({
            'temp_data': temp_data,
            'move_data': move_data
        })


class AnimalTelemetryAPIView(LoginRequiredMixin, View):
    """API endpoint returning latest telemetry for a specific animal"""
    login_url = '/auth/login/'

    def get(self, request, animal_id):
        animal = get_object_or_404(Animal, pk=animal_id)
        
        readings = SensorReading.objects.filter(animal=animal).order_by('-timestamp')[:30]
        
        temp_data = [{
            'timestamp': r.timestamp.strftime('%m-%d %H:%M'),
            'value': float(r.temperature)
        } for r in reversed(readings)]
        
        move_data = [{
            'timestamp': r.timestamp.strftime('%m-%d %H:%M'),
            'value': float(r.movement)
        } for r in reversed(readings)]
        
        return JsonResponse({
            'animal_id': animal.animal_id,
            'name': animal.name,
            'temp_data': temp_data,
            'move_data': move_data
        })


