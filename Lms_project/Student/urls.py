from django.urls import path
from . import views
from .views import StudentChangePasswordView
from django.conf import settings
from django.conf.urls.static import static

app_name = "student"

urlpatterns = [
    path("dashboard/", views.student_dashboard, name="student_dashboard"),
    path("profile/", views.StudentProfileDetailView.as_view(), name="studentprofile_detail"),
    path("profile/create/", views.StudentProfileCreateView.as_view(), name="studentprofile_create"),
    path("profile/update/", views.StudentProfileUpdateView.as_view(), name="studentprofile_update"),
    # path("courses/", views.CourseListView.as_view(), name="course_list"),
    # path("courses/<int:pk>/", views.CourseDetailView.as_view(), name="course_detail"),
    path("courses/<int:pk>/enroll/", views.EnrollCourseView.as_view(), name="enroll_course"),
    path("enrollments/", views.EnrollmentListView.as_view(), name="enrollment_list"),
    path("enrollments/<int:pk>/", views.EnrollmentDetailView.as_view(), name="enrollment_detail"),
    path("enrollments/<int:pk>/delete/", views.EnrollmentDeleteView.as_view(), name="enrollment_delete"),

    path("feedback/courses/", views.feedback_course_list, name="feedback_course_list"),
    path("feedback/<int:course_id>/", views.FeedbackCreateView.as_view(), name="feedback_create"),
    path("feedbacks/", views.FeedbackListView.as_view(), name="feedback_list"),
    path("feedback/<int:pk>/edit/", views.FeedbackUpdateView.as_view(), name="feedback_update"),

    # path("courses/<int:course_id>/feedback/", views.FeedbackCreateView.as_view(), name="feedback_create"),
    # path("feedbacks/", views.FeedbackListView.as_view(), name="feedback_list"),
    path("notifications/mark-all-read/", views.mark_all_as_read, name="mark_all_as_read"),
    path('change-password/', StudentChangePasswordView.as_view(), name='student_change_password'),
    path('courses/', views.course_list, name='course_list'),
    path('courses/<int:pk>/', views.course_detail, name='course_detail'),
    path('courses/<int:pk>/payment/', views.dummy_payment, name='dummy_payment'),
    path('courses/<int:course_id>/notes/', views.assigned_notes, name='assigned_notes'),
    path('courses/<int:course_id>/notes/<int:note_id>/', views.view_note, name='view_note'),
    #assignment URLs
    path('courses/<int:course_id>/assignments/', views.assigned_assignments, name='assigned_assignments'),
    path('courses/<int:course_id>/assignments/<int:assignment_id>/', views.view_assignment, name='view_assignment'),
    path('courses/<int:course_id>/assignments/<int:assignment_id>/submit/', views.submit_assignment, name='submit_assignment'),
    path('courses/<int:course_id>/assignments/<int:assignment_id>/edit/', views.edit_submission, name='edit_submission'),
    path('courses/<int:course_id>/assignments/<int:assignment_id>/delete/', views.delete_submission, name='delete_submission'),
    #Quiz URLs
    path('courses/<int:course_id>/quizzes/', views.student_quiz_list, name='student_quiz_list'),
    path('courses/<int:course_id>/quizzes/<int:quiz_id>/take/', views.take_quiz, name='take_quiz'),
    path('courses/<int:course_id>/quizzes/<int:quiz_id>/result/', views.quiz_result, name='quiz_result'),


    # path('courses/<int:course_id>/quizzes/', views.quiz_list, name='quiz_list'),


]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)