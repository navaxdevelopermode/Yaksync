from django.db import models
from apps.devices.models import Device
from apps.animals.models import Animal


class SensorReading(models.Model):
    """Sensor data readings from IoT devices stored as single sampling events"""
    
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='readings')
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, related_name='sensor_readings')
    temperature = models.DecimalField(max_digits=10, decimal_places=4, default=37.5)
    movement = models.DecimalField(max_digits=10, decimal_places=4, default=500.0)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    is_abnormal = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'sensor_readings'
        ordering = ['-timestamp']
        verbose_name = 'Sensor Reading'
        verbose_name_plural = 'Sensor Readings'
        indexes = [
            models.Index(fields=['animal', '-timestamp']),
        ]
    
    def save(self, *args, **kwargs):
        self.is_abnormal = False
        alert_title_temp = None
        alert_severity_temp = None
        alert_desc_temp = None
        
        alert_title_move = None
        alert_severity_move = None
        alert_desc_move = None

        # Determine temperature thresholds
        if self.temperature > 39.5:
            self.is_abnormal = True
            alert_title_temp = f"High Temperature Alert for {self.animal.animal_id}"
            alert_severity_temp = 'critical'
            alert_desc_temp = f"Yak {self.animal.name} ({self.animal.animal_id}) registered high body temperature of {self.temperature}°C (threshold: > 39.5°C)."
        elif self.temperature < 37.5:
            self.is_abnormal = True
            alert_title_temp = f"Low Temperature Alert for {self.animal.animal_id}"
            alert_severity_temp = 'warning'
            alert_desc_temp = f"Yak {self.animal.name} ({self.animal.animal_id}) registered low body temperature of {self.temperature}°C (threshold: < 37.5°C)."

        # Determine movement thresholds
        if self.movement == 0:
            self.is_abnormal = True
            alert_title_move = f"No Movement Alert for {self.animal.animal_id}"
            alert_severity_move = 'critical'
            alert_desc_move = f"Yak {self.animal.name} ({self.animal.animal_id}) registered no movement (value: 0 steps)."
        elif self.movement < 100:
            self.is_abnormal = True
            alert_title_move = f"Low Movement Alert for {self.animal.animal_id}"
            alert_severity_move = 'warning'
            alert_desc_move = f"Yak {self.animal.name} ({self.animal.animal_id}) registered low movement of {self.movement} steps (threshold: < 100 steps)."
        elif self.movement > 10000:
            self.is_abnormal = True
            alert_title_move = f"Excessive Movement Alert for {self.animal.animal_id}"
            alert_severity_move = 'warning'
            alert_desc_move = f"Yak {self.animal.name} ({self.animal.animal_id}) registered excessive movement of {self.movement} steps (threshold: > 10000 steps)."

        super().save(*args, **kwargs)

        # Create alerts if triggered
        from apps.alerts.models import Alert
        if alert_title_temp:
            Alert.objects.create(
                title=alert_title_temp,
                alert_type='temperature',
                severity=alert_severity_temp,
                description=alert_desc_temp,
                related_entity_type='animal',
                related_entity_id=self.animal.id,
                animal=self.animal,
                device=self.device,
                sensor_reading=self,
                status='active'
            )
        if alert_title_move:
            Alert.objects.create(
                title=alert_title_move,
                alert_type='movement',
                severity=alert_severity_move,
                description=alert_desc_move,
                related_entity_type='animal',
                related_entity_id=self.animal.id,
                animal=self.animal,
                device=self.device,
                sensor_reading=self,
                status='active'
            )

    def __str__(self):
        return f"Telemetry - {self.animal.animal_id} @ {self.timestamp}"

