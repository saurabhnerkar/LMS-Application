from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = "teacher"

urlpatterns = [
    path("dashboard/", views.teacher_dashboard, name="teacher_dashboard"),
    path("profile/", views.update_profile, name="update_profile"),
    path("course/view/", views.view_courses, name="view_courses"),
    path("note/add/<int:course_id>", views.add_note, name="add_note"),
    path("assignment/add/<int:course_id>/", views.add_assignment, name="add_assignment"),
    path("course_detail/<int:course_id>/", views.course_detail, name="course_detail"),
    path("teacher-profile/", views.view_profile, name="view_profile"),
    path('assignments/', views.assignment_list, name='assignments'),  # All assignments
    path('assignments/<int:course_id>/', views.assignment_list, name='course_assignments'),  # Course-specific assignments
    # Quiz URLs
    # path('quizzes/', views.quiz_list, name='quizzes'),
    path('quizzes/<int:course_id>/', views.quiz_list, name='course_quizzes'),
    path('quiz/add/<int:course_id>/', views.create_quiz, name='add_quiz'),
    path('quiz/<int:course_id>/add-question/<int:quiz_id>/', views.add_question, name='add_question'),
    path('quiz/<int:course_id>/<int:quiz_id>/delete-question/<int:question_id>/', views.delete_question, name='delete_question'),
    # path('quiz/<int:quiz_id>/', views.view_quiz, name='view_quiz'),
    path('quiz/<int:quiz_id>/', views.quiz_detail, name='quiz_detail'),
    path('quiz/<int:quiz_id>/edit/', views.edit_quiz, name='edit_quiz'),
    path('quiz/<int:quiz_id>/delete/', views.delete_quiz, name='delete_quiz'),
    path('quiz/<int:quiz_id>/submissions/', views.quiz_submissions_list, name='quiz_submissions_list'),
    # Note management URLs
    path('notes/', views.notes_list, name='notes'),  # All notes
    path('notes/<int:course_id>/', views.notes_list, name='course_notes'),  # Notes for specific course
    path('note/<int:note_id>/', views.view_note, name='view_note'),  # View single note
    path('note/<int:note_id>/edit/', views.edit_note, name='edit_note'),  # Edit note
    path('note/<int:note_id>/delete/', views.delete_note, name='delete_note'),  # Delete note
    # Assignment management URLs
    path('assignment/<int:course_id>/list/', views.course_assignments, name='course_assignments_list'),
    path('assignment/<int:assignment_id>/submissions/', views.assignment_submissions, name='assignment_submissions'),
    path('assignment/<int:assignment_id>/edit/', views.edit_assignment, name='edit_assignment'),
    path('assignment/<int:assignment_id>/delete/', views.delete_assignment, name='delete_assignment'),
    path('submission/<int:submission_id>/grade/', views.grade_submission, name='grade_submission'),
    path("notifications/mark-all-read/", views.teacher_mark_all_as_read, name="teacher_mark_all_as_read"),
    path("feedbacks/", views.teacher_feedback_list, name="teacher_feedback_list"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)