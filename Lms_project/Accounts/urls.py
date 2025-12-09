
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = "accounts"

urlpatterns = [
    path("blog/", views.blog, name="blog"),
    path("register/", views.register, name="register"),
    path("register/student/", views.register_student, name="register_student"),
    path("register/teacher/", views.register_teacher, name="register_teacher"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('resend-otp/', views.resend_otp, name='resend_otp'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
