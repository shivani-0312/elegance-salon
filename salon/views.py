# salon/views.py
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib import messages
from django.contrib.auth import login as auth_login, authenticate, logout as auth_logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import reverse,reverse_lazy
from django.contrib.auth.models import User
from .forms import CustomerRegistrationForm, LoginForm, ProfileUpdateForm,DirectPasswordResetForm,ServiceForm, ServicePackageForm
from django.contrib.auth.views import LoginView, LogoutView 
from .models import Profile, Salon, Service, ServicePackage
#3 module
from django.core.mail import send_mail
from django.conf import settings
from .models import Salon, Appointment
from .forms import AppointmentForm, RescheduleForm, CancelForm
#from .utils import send_whatsapp_message  # ✅ import
from .utils import send_appointment_email

def welcome(request):
    return render(request, 'salon/welcome.html')

def register(request):
    if request.user.is_authenticated:
        messages.info(request, "You are already logged in.")
        return redirect('salon:register')
    if request.method == 'POST':
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Successfully registered! Please log in.")
            return redirect('salon:login')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = CustomerRegistrationForm()
    return render(request, 'salon/register.html', {'form': form})

class CustomLoginView(LoginView):
    template_name = 'salon/login.html'
    authentication_form = LoginForm

    def form_valid(self, form):
        messages.success(self.request, f"Welcome back, {form.get_user().first_name or form.get_user().username}!")
        return super().form_valid(form)

class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('salon:welcome')

@login_required
def profile(request):
    user = request.user
    profile = user.profile
    if request.method == 'POST':
        pform = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        if pform.is_valid():
            # also update User basic fields
            user.first_name = pform.cleaned_data.get('first_name') or user.first_name
            user.last_name = pform.cleaned_data.get('last_name') or user.last_name
            user.email = pform.cleaned_data.get('email') or user.email
            user.save()
            pform.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('salon:profile')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        initial = {'first_name': user.first_name, 'last_name': user.last_name, 'email': user.email, 'phone': profile.phone, 'bio': profile.bio}
        pform = ProfileUpdateForm(instance=profile, initial=initial)
    return render(request, "salon/profile.html", {'pform': pform})

# Password reset class-based views (use built-in)


def direct_password_reset(request):
    success_message = None
    error_message = None

    if request.method == "POST":
        form = DirectPasswordResetForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            new_password = form.cleaned_data["new_password"]

            try:
                user = User.objects.get(username=username)
                user.set_password(new_password)
                user.save()

                success_message = "✅ Password has been reset successfully!"
                form = DirectPasswordResetForm()  # clear form

            except User.DoesNotExist:
                error_message = "❌ User not found."
        else:
            error_message = "❌ Please fix the errors below."
    else:
        form = DirectPasswordResetForm()

    return render(request, "salon/direct_password_reset.html", {
        "form": form,
        "success_message": success_message,
        "error_message": error_message,
    })


# --------- Module 2 ----------
@login_required
def salon_list(request):
    salons = Salon.objects.all()
    selections = request.session.get('selections', {})
    return render(request, 'salon/salon_list.html', {'salons': salons,'selections': selections})

@login_required
def salon_detail(request, salon_id):
    # Fetch active salon
    salon = get_object_or_404(Salon, pk=salon_id, is_active=True)

    # Fetch related services and packages
    services = salon.services.filter(is_active=True)
    packages = salon.packages.filter(is_active=True)

    # Read current selection from session
    selections = request.session.get('selections', {})
    selected = selections.get(str(salon.id), {})
    selected_services = selected.get('services', [])
    selected_package = selected.get('package', None)

    return render(request, 'salon/salon_detail.html', {
        'salon': salon,
        'services': services,
        'packages': packages,
        'selected_services': selected_services,
        'selected_package': selected_package,
    })

@login_required
def select_service(request, salon_id, service_id):
    salon = get_object_or_404(Salon, pk=salon_id, is_active=True)
    service = get_object_or_404(Service, pk=service_id, salon=salon, is_active=True)

    selections = request.session.get('selections', {})
    cur = selections.get(str(salon.id), {'services': [], 'package': None})
    # Add (toggle) service; if a package is chosen, clear it (they conflict)
    if service_id in cur['services']:
        cur['services'].remove(service_id)
        msg = f"Removed service: {service.name}"
    else:
        cur['services'].append(service_id)
        cur['package'] = None
        msg = f"Selected service: {service.name}"

    selections[str(salon.id)] = cur
    request.session['selections'] = selections
    request.session.modified = True
    messages.success(request, msg)
    return redirect('salon:salon_detail', salon_id=salon.id)

@login_required
def select_package(request, salon_id, package_id):
    salon = get_object_or_404(Salon, pk=salon_id, is_active=True)
    package = get_object_or_404(ServicePackage, pk=package_id, salon=salon, is_active=True)

    selections = request.session.get('selections', {})
    cur = selections.get(str(salon.id), {'services': [], 'package': None})
    cur['package'] = package_id
    cur['services'] = []  # clear services if package selected
    selections[str(salon.id)] = cur
    request.session['selections'] = selections
    request.session.modified = True
    messages.success(request, f"Selected package: {package.name}")
    return redirect('salon:salon_detail', salon_id=salon.id)

@login_required
def clear_selection(request, salon_id):
    selections = request.session.get('selections', {})
    if str(salon_id) in selections:
        del selections[str(salon_id)]
        request.session['selections'] = selections
        request.session.modified = True
        messages.info(request, "Selection cleared.")
    return redirect('salon:salon_detail', salon_id=salon_id)

# ---- Staff/Admin: Add/Edit Service & Package via forms (UI, not Django admin) ----
def staff_required(u):
    return u.is_staff or u.is_superuser

@login_required
@user_passes_test(staff_required)
def service_add(request):
    if request.method == 'POST':
        form = ServiceForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Service created.")
            # After creating a service, go to that salon detail
            return redirect('salon:salon_detail', salon_id=form.cleaned_data['salon'].id)
        messages.error(request, "Please correct errors below.")
    else:
        form = ServiceForm()
    return render(request, 'salon/service_form.html', {'form': form, 'title': 'Add Service'})

@login_required
@user_passes_test(staff_required)
def service_edit(request, pk):
    service = get_object_or_404(Service, pk=pk)
    if request.method == 'POST':
        form = ServiceForm(request.POST, instance=service)
        if form.is_valid():
            form.save()
            messages.success(request, "Service updated.")
            return redirect('salon:salon_detail', salon_id=service.salon.id)
        messages.error(request, "Please correct errors below.")
    else:
        form = ServiceForm(instance=service)
    return render(request, 'salon/service_form.html', {'form': form, 'title': 'Edit Service'})

@login_required
@user_passes_test(staff_required)
def package_add(request):
    if request.method == 'POST':
        form = ServicePackageForm(request.POST)
        if form.is_valid():
            pkg = form.save()
            messages.success(request, "Package created.")
            return redirect('salon:salon_detail', salon_id=pkg.salon.id)
        messages.error(request, "Please correct errors below.")
    else:
        form = ServicePackageForm()
    return render(request, 'salon/package_form.html', {'form': form, 'title': 'Create Package'})

@login_required
@user_passes_test(staff_required)
def package_edit(request, pk):
    pkg = get_object_or_404(ServicePackage, pk=pk)
    if request.method == 'POST':
        form = ServicePackageForm(request.POST, instance=pkg)
        if form.is_valid():
            form.save()
            messages.success(request, "Package updated.")
            return redirect('salon:salon_detail', salon_id=pkg.salon.id)
        messages.error(request, "Please correct errors below.")
    else:
        form = ServicePackageForm(instance=pkg)
    return render(request, 'salon/package_form.html', {'form': form, 'title': 'Edit Package'})



def book_appointment(request, salon_id):
    salon = get_object_or_404(Salon, id=salon_id)
    appointment = Appointment.objects.filter(customer=request.user, salon=salon).last()  # get latest booking
    #service = get_object_or_404(Service, id=service_id)
    
    service_id = request.GET.get("service_id")
    selected_service = None
    if service_id:
        selected_service = get_object_or_404(Service, id=service_id, salon=salon) 

    if request.method == "POST":
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.salon = salon
            appointment.customer = request.user  # assign salon
            #appointment.service = service  # assign service
            #appointment.customer = request.user 
            #appointment.form.cleaned_data["service"]
            service_id = request.POST.get("service")
            if service_id:
                service = get_object_or_404(Service, id=service_id)
                appointment.service = service
            elif selected_service:
                appointment.service = selected_service 
            appointment.save()

            # ✅ Send email
            subject = "✅ Appointment Confirmation"
            message = f"""
Hi {request.user.username},

Your appointment has been booked successfully!

Salon: {salon.name}
Service: {appointment.service}
Date: {appointment.date}
Time: {appointment.time}

Thank you for booking with us!
"""
            send_appointment_email(request.user.email, subject, message)

            messages.success(request, "Appointment booked successfully!")
            return redirect("salon:book_appointment", salon_id=salon.id)  # redirect after success
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = AppointmentForm()

    return render(request, 'salon/book_appointment.html', {
        'form': form,
        'salon': salon,
        "appointment": appointment ,
        "selected_service": selected_service,
        
    })
def appointment_success(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id,customer=request.user)
    return render(request, 'salon/appointment_success.html')

def reschedule_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, customer=request.user)

    if request.method == "POST":
        form = AppointmentForm(request.POST, instance=appointment)
        if form.is_valid():
            form.save()
            from .utils import send_appointment_email
            messages.success(request, "✅ Appointment successfully rescheduled!")
            return redirect("salon:book_appointment", salon_id=appointment.salon.id)
        else:
            messages.error(request, "❌ Please correct the errors below.")
    else:
        form = AppointmentForm(instance=appointment)

    return render(request, "salon/reschedule.html", {
        "form": form,
        "appointment": appointment,
        "salon": appointment.salon
    })


def cancel_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, customer=request.user)

    if request.method == "POST":  # user confirmed cancellation
        appointment.delete()
        # ✅ Send email
        subject = "❌ Appointment Cancelled"
        message = f"""
Hi {request.user.username},

Your appointment has been cancelled.



We hope to see you again soon!
"""
        send_appointment_email(request.user.email, subject, message)
        messages.success(request, "❌ Appointment cancelled successfully.")
        return redirect("salon:book_appointment", salon_id=appointment.salon.id)

    # if GET → show confirmation page
    return render(request, "salon/cancel.html", {
        "appointment": appointment,
        "salon": appointment.salon,
    })
