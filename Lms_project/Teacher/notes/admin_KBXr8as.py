from django.contrib import admin
from .models import TeacherProfile

@admin.register(TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'qualification_type', 'passing_year')
    search_fields = ('user__email', 'full_name')
