from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from Accounts.models import CustomUser  
from Student.models import StudentProfile
from Teacher.models import TeacherProfile

# Do NOT import models here — this causes AppRegistryNotReady

@receiver(post_save, sender=None)
def send_welcome_email(sender, instance, created, **kwargs):
   
    if sender is not CustomUser:
        return

    if created:
        subject = "Welcome to LMS!"
        message = (
            f"Hi {instance.first_name},\n\n"
            "Welcome to our Learning Management System. "
            "Your account has been created successfully!\n\n"
            "Thank you for joining us!"
        )

        send_mail(
            subject,
            message,
            'lmsproject055@gmail.com',
            [instance.email],
            fail_silently=True,
        )


@receiver(post_save, sender=None)
def create_profile_on_user_create(sender, instance, created, **kwargs):
    

    if sender is not CustomUser:
        return

    if created:
        if instance.role == "student":
            StudentProfile.objects.create(user=instance)
        elif instance.role == "teacher":
            TeacherProfile.objects.create(user=instance)


print(" Signals are loaded!")
