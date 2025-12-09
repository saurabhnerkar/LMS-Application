from django.db import models
from Accounts.models import CustomUser
from django.utils import timezone

class TeacherProfile(models.Model):
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        limit_choices_to={"role": "teacher"}, related_name="teacher_profile"
    )

    # ---- Personal Details ----
    full_name = models.CharField(max_length=255)
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')])
    mobile_number = models.CharField(max_length=10, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    bio = models.TextField(blank=True, help_text="A brief biography of the teacher.")

    # ---- Education ----
    qualification_type = models.CharField(max_length=255, null=True, blank=True)
    institution_name = models.CharField(max_length=255, null=True, blank=True)
    passing_year = models.PositiveIntegerField(null=True, blank=True)
    currently_studying = models.BooleanField(default=False)

    # ---- Work Experience ----
    prev_workplace = models.CharField(max_length=255, blank=True)
    designation = models.CharField(max_length=255, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(blank=True, null=True)
    current_joining_date = models.DateField(null=True, blank=True)
    experience = models.PositiveIntegerField(null=True, blank=True)

    # ---- Links ----
    portfolio_link = models.URLField(blank=True)
    github_link = models.URLField(blank=True)
    linkedin_link = models.URLField(blank=True)

    def __str__(self):
        return self.user.email

class Note(models.Model):
    teacher = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role': 'teacher'}, null=True, blank=True)
    course = models.ForeignKey('Courses.Course', on_delete=models.CASCADE, related_name='notes')
    title = models.CharField(max_length=100)
    content = models.TextField()
    upload_file = models.FileField(upload_to='teacher/notes/', blank=True, null=True)
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.course.name})"

class TeacherAssignment(models.Model):
    teacher = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role': 'teacher'}, null=True, blank=True)
    course = models.ForeignKey('Courses.Course', on_delete=models.CASCADE, related_name='assignments')
    title = models.CharField(max_length=100)
    instructions = models.TextField()
    due_date = models.DateField()
    created_on = models.DateTimeField(auto_now_add=True)
    upload_file = models.FileField(upload_to='teacher/assignments/', blank=True, null=True)

    def __str__(self):
        return f"{self.title} ({self.course.title})"
    
class Quiz(models.Model):
    teacher = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role': 'teacher'}, null=True, blank=True)
    course = models.ForeignKey('Courses.Course', on_delete=models.CASCADE, related_name='quizzes')
    title = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    total_marks = models.PositiveIntegerField(default=100)
    time_limit_minutes = models.PositiveIntegerField(null=True, blank=True, help_text='Time limit in minutes (optional)')

    # ----- New fields for active period -----
    start_time = models.DateTimeField(null=True, blank=True, help_text="Quiz start date and time")
    end_time = models.DateTimeField(null=True, blank=True, help_text="Quiz end date and time")

    created_on = models.DateTimeField(auto_now_add=True)

    def is_active(self):
        now = timezone.now()
        if self.start_time and self.end_time:
            return self.start_time <= now <= self.end_time
        return False

    def has_started(self):
        now = timezone.now()
        if self.start_time:
            return now >= self.start_time
        return True  # default: started if no start_time

    def has_ended(self):
        now = timezone.now()
        if self.end_time:
            return now > self.end_time
        return False

class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    marks = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.text

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)
    
    def __str__(self):
        return self.text