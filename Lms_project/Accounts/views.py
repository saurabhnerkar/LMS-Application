from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from .models import *
from .forms import *
from django.views.decorators.csrf import csrf_protect
from django.core.cache import cache
import random



def blog(request):
    return render(request, "blog.html")

def register(request):
    return render(request, "accounts/register.html")


def register_student(request):
    next_url = request.GET.get('next', '')

    if request.method == "POST":
        user_form = StudentRegistrationForm(request.POST, request.FILES)
        profile_form = StudentProfileForm(request.POST)
        next_url = request.POST.get('next', '')

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save(commit=False)
            user.role = "student"
            user.save()

            send_otp_email(user)
            messages.success(request, "Account created. Check email for OTP.")
            request.session["pending_user_id"] = user.id
            if next_url:
                request.session["pending_next_url"] = next_url

            return redirect("accounts:verify_otp")

    else:
        user_form = StudentRegistrationForm()
        profile_form = StudentProfileForm()

    return render(
        request,
        "accounts/register_student.html",
        {"user_form": user_form, "profile_form": profile_form, "next": next_url}
    )


def register_teacher(request):
    if request.method == "POST":
        user_form = TeacherRegistrationForm(request.POST, request.FILES)
        if user_form.is_valid():
            user = user_form.save(commit=False)
            user.role = "teacher"
            user.save()
            send_otp_email(user)
            messages.success(request, "Account created. Check email for OTP.")
            request.session["pending_user_id"] = user.id
            return redirect("accounts:verify_otp")
    else:
        user_form = TeacherRegistrationForm()
    return render(request, "accounts/register_teacher.html", {"user_form": user_form})


def login_view(request):
    if request.method == "POST":
        form = LoginForm(request, data=request.POST)

        email = request.POST.get("username")
        ip = request.META.get("REMOTE_ADDR")
        attempt_key = f"login_attempts_{email}_{ip}"
        attempts = cache.get(attempt_key, 0)
        if attempts >= 5:
            messages.error(request, "Too many failed attempts. Try again after 1 hour.")
            return render(request, "accounts/login.html", {"form": form})

        if form.is_valid():
            password = form.cleaned_data.get("password")
            role = form.cleaned_data.get("role")

            user = authenticate(request, username=email, password=password)
            if user is None:
                attempts += 1
                cache.set(attempt_key, attempts, timeout=3600)  # Lock time = 1 hour
                remaining = 5 - attempts
                if remaining > 0:
                    messages.error(request, f"Invalid credentials. {remaining} attempts left.")
                else:
                    messages.error(request, "Too many failed attempts. Account locked for 1 hour.")
                return render(request, "accounts/login.html", {"form": form})

            if user.role != role:
                messages.error(request, f"You are not registered as a {role}.")
                return render(request, "accounts/login.html", {"form": form})

        
            if not user.is_email_verified and role != "admin":
                send_otp_email(user)
                request.session["pending_user_id"] = user.id
                request.session["login_after_otp"] = False
                messages.info(request, "Email not verified. OTP sent.")
                return redirect("accounts:verify_otp")

          
            cache.delete(attempt_key)
            send_otp_email(user)
            request.session["pending_user_id"] = user.id
            request.session["login_after_otp"] = True
            messages.info(request, "OTP sent for login verification.")
            return redirect("accounts:verify_otp")

        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = LoginForm(request)

    return render(request, "accounts/login.html", {"form": form})



def logout_view(request):
    logout(request)
    return redirect("home")


def send_otp_email(user):
    otp = str(random.randint(100000, 999999))

    # Store OTP in Redis (expires in 5 minutes)
    cache.set(f"otp_{user.id}", otp, timeout=300)

    send_mail(
        'Your LMS Login OTP',
        f'Hi {user.first_name}, your OTP is {otp}. It is valid for 5 minutes.',
        'youremail@gmail.com',
        [user.email],
        fail_silently=False,
    )

def verify_otp(request):
    pending_user_id = request.session.get("pending_user_id")
    if not pending_user_id:
        messages.error(request, "No pending user found for OTP verification.")
        return redirect("accounts:login")

    try:
        user = CustomUser.objects.get(id=pending_user_id)
    except CustomUser.DoesNotExist:
        messages.error(request, "User not found.")
        return redirect("accounts:login")

    if request.method == "POST":
        otp_input = request.POST.get("otp")   
        saved_otp = cache.get(f"otp_{user.id}")

        if not saved_otp:
            messages.error(request, "OTP expired or not found.")
            return redirect("accounts:verify_otp")

        if otp_input == saved_otp:
           
            cache.delete(f"otp_{user.id}")

           
            if request.session.get("login_after_otp") == True:
                login(request, user)
                messages.success(request, "Login successful!")
                request.session.pop("pending_user_id", None)
                request.session.pop("login_after_otp", None)
                return _redirect_by_role(user)

           
            user.is_email_verified = True
            user.save(update_fields=["is_email_verified"])

            login(request, user)
            messages.success(request, "OTP verified successfully!")
            request.session.pop("pending_user_id", None)

            return _redirect_by_role(user)

        else:
            messages.error(request, "Invalid OTP entered.")

    return render(request, "accounts/verify_otp.html", {"email": user.email})

def resend_otp(request):
    pending_user_id = request.session.get('pending_user_id')
    if not pending_user_id:
        messages.warning(request, "No pending user for OTP resend.")
        return redirect("accounts:verify_otp")

    try:
        user = CustomUser.objects.get(id=pending_user_id)
    except CustomUser.DoesNotExist:
        messages.error(request, "User not found.")
        return redirect("accounts:verify_otp")
  
    send_otp_email(user)

    messages.info(request, "A new OTP has been sent to your email.")
    return redirect("accounts:verify_otp")


def _redirect_by_role(user: CustomUser):
    if user.role == "student":
        return redirect("student:student_dashboard")
    elif user.role == "teacher":
        return redirect("teacher:teacher_dashboard")
    elif user.role == "admin":
        return redirect("/admin/")  
    else:
        return redirect("home")


