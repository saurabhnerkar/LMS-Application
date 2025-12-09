
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from Student.models import  StudentProfile
from Teacher.models import   TeacherProfile
from .models import CustomUser, LoginOTP

# Customize the UserAdmin for CustomUser
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'role', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_active')
    search_fields = ('username', 'email')
    ordering = ('username',)
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password', 'role', 'profile_picture', 'is_email_verified')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Email Verification', {'fields': ('email_verification_token',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'role', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )

# Register models with admin
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(StudentProfile)
admin.site.register(LoginOTP)
