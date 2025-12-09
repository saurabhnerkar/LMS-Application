from django.db import models
from django.utils import timezone
from Accounts.models import CustomUser
from Teacher.models import TeacherAssignment
from Courses.models import Course

class StudentProfile(models.Model):
    user = models.OneToOneField( 
        CustomUser,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'student'},
        related_name='student_profile'
    )
    address = models.CharField(max_length=255, blank=True)
    mobile_number = models.CharField(max_length=15, blank=True)
    educational_background = models.CharField(max_length=255, blank=True)
    passing_year = models.PositiveIntegerField(blank=True, null=True)
    bio = models.TextField(blank=True)

    def __str__(self):
        return f"Student: {self.user.email}"

# class Course(models.Model):
#     name = models.CharField(max_length=255)
#     description = models.TextField(blank=True)
#     price = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
#     instructor = models.ForeignKey(
#         'Teacher.TeacherProfile',  
#         on_delete=models.SET_NULL,
#         null=True,
#         blank=True,
#         related_name='student_courses'
#     )

#     def __str__(self):
#         return self.name
    
class Enrollment(models.Model):
    student = models.ForeignKey('StudentProfile', on_delete=models.CASCADE)
    course = models.ForeignKey('Courses.Course', on_delete=models.CASCADE, related_name="enrollments")  # Use correct model reference
    enrollment_date = models.DateTimeField(auto_now_add=True)
    payment_completed = models.BooleanField(default=False)

    class Meta:
        unique_together = ['student', 'course']

    def __str__(self):
        return f"{self.student} enrolled in {self.course.title}"  # Changed from name to title

class ClassSession(models.Model):
    course = models.ForeignKey('Courses.course', on_delete=models.CASCADE, related_name='classes')
    date_time = models.DateTimeField()
    topic = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.course.name} - {self.date_time.strftime('%b %d, %Y %H:%M')}"

class AssignmentSubmission(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name='submissions')
    assignment = models.ForeignKey(TeacherAssignment, on_delete=models.CASCADE, related_name='submissions', null=True, blank=True)
    file = models.FileField(upload_to='assignments/')
    submitted_on = models.DateTimeField(auto_now_add=True)
    grade = models.CharField(max_length=10, blank=True)
    remarks = models.TextField(blank=True)

    def __str__(self):
        return f"Submission #{self.id} by {self.enrollment.student.user.email}"

class Feedback(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="course_feedbacks")
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name="student_feedbacks")
    relevance_rating = models.IntegerField()                 
    trainer_knowledge_rating = models.IntegerField()         
    overall_satisfaction_rating = models.IntegerField()      
    material_easy = models.CharField(max_length=50)          
    duration_appropriate = models.CharField(max_length=50)   
    achieved_objective = models.CharField(max_length=50)     
    recommend_trainer = models.CharField(max_length=50)     
    improvement_suggestions = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.course.title} Feedback"

    

class Notification(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notif for {self.user.email}: {self.message[:20]}"
    
class QuizSubmission(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name='quiz_submissions')
    quiz = models.ForeignKey('Teacher.Quiz', on_delete=models.CASCADE, related_name='submissions')
    score = models.PositiveIntegerField()
    submitted_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Quiz Submission #{self.id} by {self.enrollment.student.user.email}"
    
class QuizAnswer(models.Model):
    submission = models.ForeignKey(QuizSubmission, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey('Teacher.Question', on_delete=models.CASCADE)
    selected_option = models.ForeignKey('Teacher.Choice', on_delete=models.CASCADE)
    is_correct = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.is_correct = self.selected_option.is_correct
        super().save(*args, **kwargs)
