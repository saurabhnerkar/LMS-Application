# Course/forms.py
from django import forms
from .models import Course
from Teacher.models import TeacherProfile

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'description', 'teacher', 'course_image']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'teacher': forms.Select(attrs={'class': 'form-control'}),
            'course_image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
