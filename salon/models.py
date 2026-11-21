# salon/models.py
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
#from salon.models import Salon, Service
#from django.utils import timezone
GENDER_CHOICES = (
    ('M', 'Male'),
    ('F', 'Female'),
    ('O', 'Other'),
)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, blank=True, null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)
    bio = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user.username} Profile"

    def get_absolute_url(self):
        return reverse('salon:profile')
# ---- Module 2 models ----
class Salon(models.Model):
    name = models.CharField(max_length=120)
    area = models.CharField(max_length=120, blank=True)
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='salons/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('salon:salon_detail', args=[self.id])

SERVICE_CATEGORIES = (
    ('HAIR', 'Hair'),
    ('SKIN', 'Skin'),
    ('MAKEUP', 'Makeup'),
    ('SPA', 'Spa'),
    ('NAILS', 'Nails'),
    ('OTHER', 'Other'),
)

class Service(models.Model):
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE, related_name='services')
    name = models.CharField(max_length=120)
    category = models.CharField(max_length=20, choices=SERVICE_CATEGORIES, default='OTHER')
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    duration = models.PositiveIntegerField(help_text="Minutes")
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('salon', 'name')
        ordering = ['category', 'name']

    def __str__(self):
        return f"{self.name} ({self.salon.name})"

class ServicePackage(models.Model):
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE, related_name='packages')
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    services = models.ManyToManyField(Service, related_name='included_in_packages')
    price = models.DecimalField(max_digits=8, decimal_places=2)
    duration = models.PositiveIntegerField(help_text="Total minutes")
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('salon', 'name')
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.salon.name})"
    
    #3 module


class Appointment(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    email = models.EmailField(blank=True, null=True)
    date = models.DateField()
    time = models.TimeField()
    notes = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE, default=1)  # <-- Add this line

    def __str__(self):
#def __str__(self):
         return f"{self.customer.username} - {self.service} on {self.date.strftime('%Y-%m-%d')}"
