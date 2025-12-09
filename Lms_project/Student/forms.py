from django import forms
from .models import StudentProfile, Enrollment, AssignmentSubmission, Feedback

# class StudentProfileForm(forms.ModelForm):
#     class Meta:
#         model = StudentProfile
#         fields = ['address','mobile_number','educational_background','passing_year','bio']


class StudentProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50)
    email = forms.EmailField()
    username = forms.CharField(max_length=50)

    class Meta:
        model = StudentProfile
        fields = ["address", "mobile_number", "educational_background", "passing_year", "bio"]

class EnrollmentForm(forms.ModelForm):
    class Meta:
        model = Enrollment
        fields = ['course']

class AssignmentSubmissionForm(forms.ModelForm):
    class Meta:
        model = AssignmentSubmission
        fields = ['file']

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['course']