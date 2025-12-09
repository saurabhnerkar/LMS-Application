from Student.models import Enrollment, Notification
from django.core.mail import send_mail
from django.conf import settings

def notify_students(course, message):
    """Send notification to all students enrolled in the course."""
    enrollments = Enrollment.objects.filter(course=course)
    for e in enrollments:
        Notification.objects.create(
            user=e.student.user,
            message=message
        )

def notify_teacher(course, message, email_notify=False):
    """Send a notification to the teacher of a course."""
    teacher_user = course.teacher.user
    Notification.objects.create(user=teacher_user, message=message)

    if email_notify and teacher_user.email:
        send_mail(
            subject=f"Course Update: {course.title}",
            message=message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[teacher_user.email],
            fail_silently=True,
        )
