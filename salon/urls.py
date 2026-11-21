# salon/urls.py
from django.urls import path
from . import views

app_name = 'salon'

urlpatterns = [
    path('', views.welcome, name='welcome'),
    path('register/', views.register, name='register'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('profile/', views.profile, name='profile'),

    # password reset
     path("password-reset/", views.direct_password_reset, name="password_reset"),

    # Module 2: Salons / Services / Packages
    #path('module2/', views.salon_list, name='salon_list'),  # <- login redirect target
    path('salons/', views.salon_list, name='salon_list'),
    path('salons/<int:salon_id>/', views.salon_detail, name='salon_detail'),
    path('salons/<int:salon_id>/select-service/<int:service_id>/', views.select_service, name='select_service'),
    path('salons/<int:salon_id>/select-package/<int:package_id>/', views.select_package, name='select_package'),
    path('salons/<int:salon_id>/clear-selection/', views.clear_selection, name='clear_selection'),
    path("salons/<int:salon_id>/book/", views.book_appointment, name="booking_start"),

    path('salons/<int:salon_id>/book/', views.book_appointment, name='book_appointment'),
    # other urls
    path('appointment-success/', views.appointment_success, name='appointment_success'),
    path("appointments/<int:appointment_id>/reschedule/", views.reschedule_appointment, name="reschedule"),
    path("appointments/<int:appointment_id>/cancel/", views.cancel_appointment, name="cancel"),

    # Staff/Admin side
    path('staff/service/add/', views.service_add, name='service_add'),
    path('staff/service/<int:pk>/edit/', views.service_edit, name='service_edit'),
    path('staff/package/add/', views.package_add, name='package_add'),
    path('staff/package/<int:pk>/edit/', views.package_edit, name='package_edit'),

]

