from django.db import models
class Course(models.Model):
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to="courses/", blank=True, null=True) 
    description = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    more_info = models.TextField(blank=True, null=True)
    # Use string reference for TeacherProfile to avoid circular import
    teacher = models.ForeignKey(
        'Teacher.TeacherProfile',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="courses"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
