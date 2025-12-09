from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from datetime import timedelta
from django.utils import timezone
from .models import *
from .forms import *
from django.views.decorators.csrf import csrf_protect

# Create your views here.


# Blog
def blog(request):
    return render(request, "blog.html")

def register(request):
    return render(request, "accounts/register.html")

def register_student(request):
    next_url = request.GET.get('next', '')  # Get next parameter from GET

    if request.method == "POST":
        user_form = StudentRegistrationForm(request.POST, request.FILES)
        profile_form = StudentProfileForm(request.POST)
        next_url = request.POST.get('next', '')  # Get next from POST as well
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save(commit=False)
            user.role = "student"
            user.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            from django.conf import settings
            import pprint
            print("=== EMAIL CONFIG DEBUG ===")
            pprint.pprint({
                "EMAIL_HOST": settings.EMAIL_HOST,
                "EMAIL_PORT": settings.EMAIL_PORT,
                "EMAIL_HOST_USER": settings.EMAIL_HOST_USER,
                "EMAIL_BACKEND": settings.EMAIL_BACKEND,
                })
            print("==========================")
            send_otp_email(user)
            messages.success(request, "Account created. Check email for OTP.")
            request.session["pending_user_id"] = user.id
            # Save next_url in session to use after OTP verification
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

# views.py

def login_view(request):
    if request.method == "POST":
        print("Login POST request received")
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            print("Login form is valid")
            email = form.cleaned_data.get("username")  # This will now be email
            password = form.cleaned_data.get("password")
            role = form.cleaned_data.get("role")

            user = authenticate(request, username=email, password=password)

            if user is None:
                messages.error(request, "Invalid email or password.")
            elif user.role != role:
                messages.error(request, f"You are not registered as a {role}.")
            elif not user.is_email_verified and role != "admin":
                # Only apply OTP verification for non-admin users
                send_otp_email(user)
                request.session["pending_user_id"] = user.id
                messages.info(request, "Email not verified. OTP sent.")
                return redirect("accounts:verify_otp")
            else:
                login(request, user)
                return _redirect_by_role(user)
        else:
            print("Form is invalid — errors:", form.errors)
            messages.error(request, "Please correct the errors below.")
    else:
        form = LoginForm(request)
    return render(request, "accounts/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("home")

def send_otp_email(user):
    otp = str(random.randint(100000, 999999))
    expires_at = timezone.now() + timedelta(minutes=5)

    # create OTP record
    LoginOTP.objects.create(user=user, otp=otp, expires_at=expires_at)

    # send OTP to email
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

    if request.method == 'POST':
        otp_input = request.POST.get('otp')
        otp_record = LoginOTP.objects.filter(user=user, is_used=False).order_by('-created_at').first()

        if not otp_record:
            messages.error(request, 'No OTP found or already used.')
        elif otp_record.is_expired():
            messages.error(request, 'OTP expired! Please request again.')
        elif otp_record.otp == otp_input:
            otp_record.is_used = True
            otp_record.save(update_fields=['is_used'])
            user.is_email_verified = True
            user.save(update_fields=['is_email_verified'])
            login(request, user)
            messages.success(request, 'OTP verified successfully!')
            request.session.pop('pending_user_id', None)
            return _redirect_by_role(user)
        else:
            messages.error(request, 'Invalid OTP entered.')

    return render(request, 'accounts/verify_otp.html', {"email": user.email})

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
        return redirect("/admin/")  # built-in Django admin panel
    else:
        return redirect("home")


