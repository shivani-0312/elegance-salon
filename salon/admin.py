## salon/admin.py
from django.contrib import admin
from .models import Profile,Salon, Service, ServicePackage

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'gender')
@admin.register(Salon)
class SalonAdmin(admin.ModelAdmin):
    list_display = ('name', 'area', 'phone', 'is_active')
    search_fields = ('name','area')

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name','salon','category','price','duration','is_active')
    list_filter = ('salon','category','is_active')
    search_fields = ('name',)

@admin.register(ServicePackage)
class ServicePackageAdmin(admin.ModelAdmin):
   list_display = ('name','salon','price','duration','is_active')
   list_filter = ('salon','is_active')
   search_fields = ('name',)
    #filter_horizontal = ('services',)