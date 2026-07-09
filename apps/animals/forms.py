from django import forms
from .models import Animal


class AnimalForm(forms.ModelForm):
    """Form for creating and updating animals"""
    
    class Meta:
        model = Animal
        fields = [
            'animal_id', 'name', 'species', 'breed', 'date_of_birth', 'gender', 
            'weight', 'health_status', 'reproductive_status', 'dam', 'sire', 
            'breeding_method', 'vulva_length', 'vaginal_depth', 
            'distance_to_cervix', 'vaginal_diameter', 'parity', 'vagina_temperature', 
            'description'
        ]
        widgets = {
            'animal_id': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g., YAK697',
                'required': True,
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Animal name',
                'required': True,
            }),
            'species': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g., Yak, Cattle',
                'required': True,
            }),
            'breed': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g., Highland Yak',
                'required': True,
            }),
            'date_of_birth': forms.DateInput(attrs={
                'class': 'form-input',
                'type': 'date',
                'required': True,
            }),
            'weight': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': 'Weight in kg',
                'required': True,
                'step': '0.01',
                'min': '0',
            }),
            'health_status': forms.Select(attrs={
                'class': 'form-input',
                'required': True,
            }),
            'reproductive_status': forms.Select(attrs={
                'class': 'form-input',
                'required': True,
            }),
            'dam': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Dam ID',
            }),
            'sire': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Sire ID',
            }),
            'breeding_method': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g., Natural, Artificial Insemination',
            }),
            'vulva_length': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': 'Vulva Length in cm',
                'step': '0.01',
                'min': '0',
            }),
            'vaginal_depth': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': 'Vaginal Depth in cm',
                'step': '0.01',
                'min': '0',
            }),
            'distance_to_cervix': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': 'Distance to Cervix in cm',
                'step': '0.01',
                'min': '0',
            }),
            'vaginal_diameter': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': 'Vaginal Diameter in cm',
                'step': '0.01',
                'min': '0',
            }),
            'parity': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': 'Parity count',
                'min': '0',
            }),
            'vagina_temperature': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': 'Vaginal Temperature in °C',
                'step': '0.01',
                'min': '0',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-input',
                'placeholder': 'Physical markings, color pattern, horn status, etc.',
                'rows': 3,
            }),
        }
        labels = {
            'animal_id': 'Animal ID',
            'name': 'Name',
            'species': 'Species',
            'breed': 'Breed',
            'date_of_birth': 'Date of Birth',
            'gender': 'Gender',
            'weight': 'Weight (kg)',
            'health_status': 'Health Status',
            'reproductive_status': 'Reproductive Status',
            'dam': 'Dam ID',
            'sire': 'Sire ID',
            'breeding_method': 'Breeding Method',
            'vulva_length': 'Vulva Length (cm)',
            'vaginal_depth': 'Vaginal Depth (cm)',
            'distance_to_cervix': 'Distance to Cervix (cm)',
            'vaginal_diameter': 'Vaginal Diameter (cm)',
            'parity': 'Parity count',
            'vagina_temperature': 'Vaginal Temperature (°C)',
            'description': 'Physical Description',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['gender'].initial = 'female'
        self.fields['gender'].widget = forms.HiddenInput(attrs={'value': 'female'})
        self.fields['species'].initial = 'Yak'
        self.fields['breed'].initial = 'Yak'
    
    def clean_animal_id(self):
        animal_id = self.cleaned_data.get('animal_id')
        # Check for uniqueness, excluding current instance during updates
        qs = Animal.objects.filter(animal_id=animal_id)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError('This Animal ID already exists.')
        return animal_id
    
    def clean_date_of_birth(self):
        date_of_birth = self.cleaned_data.get('date_of_birth')
        if date_of_birth:
            from datetime import date
            today = date.today()
            if date_of_birth > today:
                raise forms.ValidationError('Date of birth cannot be in the future.')
            age = today.year - date_of_birth.year - (
                (today.month, today.day) < (date_of_birth.month, date_of_birth.day)
            )
            if age > 30:
                raise forms.ValidationError('Age based on DOB seems unusually high. Please verify.')
        return date_of_birth
    
    def clean_weight(self):
        weight = self.cleaned_data.get('weight')
        if weight is not None and weight <= 0:
            raise forms.ValidationError('Weight must be greater than 0.')
        return weight
