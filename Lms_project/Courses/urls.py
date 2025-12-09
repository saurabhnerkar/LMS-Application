# Course/urls.py
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'course'

urlpatterns = [
    # Admin routes
    path('admin/courses/', views.admin_course_list, name='admin_course_list'),
    path('admin/courses/add/', views.create_course, name='create_course'),
    path('admin/courses/edit/<int:pk>/', views.edit_course, name='edit_course'),
    path('admin/courses/delete/<int:pk>/', views.delete_course, name='delete_course'),

    # Teacher route
    path('teacher/dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
