from django.db import models
from django.contrib.auth.models import User


class FemaleAnimalManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(gender='female')


class Animal(models.Model):
    """Livestock animal records"""
    
    objects = FemaleAnimalManager()
    all_objects = models.Manager()

    
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
    ]
    
    HEALTH_STATUS_CHOICES = [
        ('healthy', 'Healthy'),
        ('sick', 'Sick'),
        ('under_treatment', 'Under Treatment'),
    ]
    
    REPRODUCTIVE_STATUS_CHOICES = [
        ('pregnant', 'Pregnant'),
        ('cycling', 'Cycling'),
        ('not_cycling', 'Not Cycling'),
    ]
    
    animal_id = models.CharField(max_length=50, unique=True, db_index=True)
    name = models.CharField(max_length=100)
    species = models.CharField(max_length=50)
    breed = models.CharField(max_length=100)
    age = models.IntegerField()
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    weight = models.DecimalField(max_digits=6, decimal_places=2)
    health_status = models.CharField(max_length=50, choices=HEALTH_STATUS_CHOICES, default='healthy')
    reproductive_status = models.CharField(max_length=50, choices=REPRODUCTIVE_STATUS_CHOICES)
    
    # New Yak fields
    date_of_birth = models.DateField(null=True, blank=True)
    dam = models.CharField(max_length=50, null=True, blank=True)
    sire = models.CharField(max_length=50, null=True, blank=True)
    breeding_method = models.CharField(max_length=50, null=True, blank=True)
    vulva_length = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    vaginal_depth = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    distance_to_cervix = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    vaginal_diameter = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    parity = models.IntegerField(null=True, blank=True)
    vagina_temperature = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    registration_date = models.DateField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='animals_created')
    
    class Meta:
        db_table = 'animals'
        ordering = ['-created_at']
        verbose_name = 'Animal'
        verbose_name_plural = 'Animals'
    
    def __str__(self):
        return f"{self.animal_id} - {self.name}"

    def save(self, *args, **kwargs):
        if self.date_of_birth:
            from datetime import date
            today = date.today()
            self.age = today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
            )
        else:
            if not self.age:
                self.age = 0
        super().save(*args, **kwargs)
