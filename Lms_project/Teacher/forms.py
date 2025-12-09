from django import forms
from .models import TeacherProfile, Note, TeacherAssignment
from Courses.models import Course
from .models import Quiz, Question, Choice  
from Student.models import AssignmentSubmission
from django.forms import inlineformset_factory
class TeacherProfileForm(forms.ModelForm):

    # Add user fields manually
    first_name = forms.CharField(max_length=150, required=False)
    last_name = forms.CharField(max_length=150, required=False)
    username = forms.CharField(max_length=150, required=False)
    email = forms.EmailField(required=False)

    class Meta:
        model = TeacherProfile
        fields = [
            # USER FIELDS
            "first_name", "last_name", "username", "email",

            # PROFILE FIELDS (your old fields)
            "full_name", "gender", "mobile_number", "date_of_birth",
            "country", "state", "address", "bio",
            "qualification_type", "institution_name", "passing_year", "currently_studying",
            "prev_workplace", "designation", "start_date", "end_date",
            "current_joining_date", "experience",
            "portfolio_link", "github_link", "linkedin_link"
        ]
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
            "current_joining_date": forms.DateInput(attrs={"type": "date"}),
        }


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'description']

class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ['title', 'content', 'upload_file']

class TeacherAssignmentForm(forms.ModelForm):
    class Meta:
        model = TeacherAssignment
        fields = ['title', 'instructions', 'due_date', 'upload_file']

        widgets = {
            'due_date': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'form-control',
                    'placeholder': 'Select due date'
                }
                ),
            }
            
class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ['title', 'description', 'total_marks', 'time_limit_minutes', 'start_time', 'end_time']
        widgets = {
                'description': forms.Textarea(attrs={'rows': 4}),
                'total_marks': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
                'time_limit_minutes': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
                'start_time': forms.DateTimeInput(attrs={'type':'datetime-local', 'class':'form-control'}),
                'end_time': forms.DateTimeInput(attrs={'type':'datetime-local', 'class':'form-control'}),
            }
            
class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['text', 'marks']
        widgets = {
                'text': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
                'marks': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            }


class GradeSubmissionForm(forms.ModelForm):
    class Meta:
        model = AssignmentSubmission
        fields = ['grade', 'remarks']
        widgets = {
                'grade': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter grade (e.g. A, B+, 95%)'}),
                'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter remarks'}),
            }
            
from django.forms import inlineformset_factory, BaseInlineFormSet

class BaseChoiceFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        correct_choices = 0
        for form in self.forms:
            if not form.cleaned_data or form.cleaned_data.get('DELETE', False):
                continue
            if form.cleaned_data.get('is_correct'):
                correct_choices += 1

            if correct_choices == 0:
                raise forms.ValidationError("Please mark at least one correct answer.")
            if correct_choices > 1:
                raise forms.ValidationError("Only one option can be correct.")

ChoiceFormSet = inlineformset_factory(
    Question,
    Choice,
    fields=('text', 'is_correct'),
    extra=4,
    can_delete=True,
    formset=BaseChoiceFormSet,  # 👈 use the custom validation class here
    widgets={
            'text': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Option text'}),
            'is_correct': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    )
