# salon/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Profile,Salon, Service, ServicePackage
from .models import Appointment
from django.core.exceptions import ValidationError
import datetime
import re

class CustomerRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text='Required. Enter a valid email address.')
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=False)
    phone = forms.CharField(max_length=15, required=True, help_text='Digits only, min 7 max 15')

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'phone', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("That email address is already registered.")
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '')
        phone_digits = re.sub(r'\D', '', phone)
        if len(phone_digits) < 7 or len(phone_digits) > 15:
            raise forms.ValidationError("Enter a valid phone number (7–15 digits).")
        return phone_digits

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            # create/update profile phone
            profile = Profile.objects.get(user=user)
            profile.phone = self.cleaned_data['phone']
            profile.save()
        return user

class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'autofocus': True}))
    password = forms.CharField(widget=forms.PasswordInput)

class ProfileUpdateForm(forms.ModelForm):
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=False)
    email = forms.EmailField(required=True)
    phone = forms.CharField(required=False)
    profile_image = forms.ImageField(required=False)
    bio = forms.CharField(widget=forms.Textarea, required=False)

    class Meta:
        model = Profile
        fields = ('phone', 'gender', 'profile_image', 'bio')

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '')
        phone_digits = re.sub(r'\D', '', phone)
        if phone and (len(phone_digits) < 7 or len(phone_digits) > 15):
            raise forms.ValidationError("Enter a valid phone number (7–15 digits).")
        return phone_digits

class DirectPasswordResetForm(forms.Form):
    username = forms.CharField(max_length=150, label="Username")
    new_password = forms.CharField(
        widget=forms.PasswordInput, 
        label="New Password"
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput, 
        label="Confirm Password"
    )

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("new_password")
        password2 = cleaned_data.get("confirm_password")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match ❌")

        return cleaned_data




class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['salon','name','category','description','price','duration','is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows':3}),
        }
    def clean(self):
        cleaned = super().clean()
        if cleaned.get('price') is not None and cleaned['price'] <= 0:
            self.add_error('price', 'Price must be greater than 0.')
        if cleaned.get('duration') is not None and cleaned['duration'] <= 0:
            self.add_error('duration', 'Duration must be a positive number of minutes.')
        return cleaned

class ServicePackageForm(forms.ModelForm):
    class Meta:
        model = ServicePackage
        fields = ['salon','name','description','services','price','duration','is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows':3}),
            'services': forms.CheckboxSelectMultiple(),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # if a salon already chosen, filter services to that salon
        salon = None
        if 'salon' in self.data:
            try:
                salon = int(self.data.get('salon'))
            except Exception:
                salon = None
        elif self.instance and self.instance.pk:
            salon = self.instance.salon_id
        if salon:
            self.fields['services'].queryset = Service.objects.filter(salon_id=salon, is_active=True)
        else:
            self.fields['services'].queryset = Service.objects.none()
    def clean(self):
        cleaned = super().clean()
        if cleaned.get('price') is not None and cleaned['price'] <= 0:
            self.add_error('price', 'Price must be greater than 0.')
        if cleaned.get('duration') is not None and cleaned['duration'] <= 0:
            self.add_error('duration', 'Duration must be a positive number of minutes.')
        return cleaned
# 3 module


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        exclude = ['customer', 'salon','status','created_at']  
        fields = ['date', 'time', 'phone', 'email','service']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Phone Number'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter Email'}),
        }
        #dfd
    def clean_date(self):
        date = self.cleaned_data['date']
        if date < datetime.date.today():
            raise ValidationError("Date cannot be in the past.")
        return date

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        if not phone.isdigit() or len(phone) != 10:
            raise ValidationError("Enter a valid 10-digit phone number.")
        return phone

class RescheduleForm(forms.ModelForm):
    date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=True
    )
    time = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time'}),
        required=True
    )

    class Meta:
        model = Appointment
        fields = ["date", "time"]
    def clean(self):
     cleaned_data = super().clean()
     date = cleaned_data.get("date")
     time = cleaned_data.get("time")

     if not date:
        self.add_error("date", "Please select a new date.")
     if not time:
        self.add_error("time", "Please select a new time.")

     return cleaned_data


class CancelForm(forms.Form):
    confirm = forms.BooleanField(
        required=True,
        label="I confirm that I want to cancel this appointment."
    )