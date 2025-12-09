# from django import forms
# from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
# from .models import CustomUser
# from Student.models import StudentProfile
# from Teacher.models import TeacherProfile

# class StudentRegistrationForm(UserCreationForm):
#     email = forms.EmailField(max_length=254, help_text='Required. Enter a valid email address.')
    
#     class Meta(UserCreationForm.Meta):
#         model = CustomUser
#         fields = ('email', 'profile_picture')

# class StudentProfileForm(forms.ModelForm):
#     class Meta:
#         model = StudentProfile
#         fields = ('address', 'mobile_number', 'educational_background', 'passing_year', 'bio')

# class TeacherRegistrationForm(forms.ModelForm):
#     class Meta:
#         model = TeacherProfile
#         fields = [
#             "full_name", "gender", "mobile_number", "date_of_birth",
#             "country", "state", "address", "bio",
#             "qualification_type", "institution_name", "passing_year", "currently_studying"
#         ]
#         widgets = {
#             "date_of_birth": forms.DateInput(attrs={"type": "date"}),
#         }

# class TeacherProfileForm(forms.ModelForm):
#     class Meta:
#         model = TeacherProfile
#         fields = [
#             "bio",
#             "prev_workplace", "designation", "start_date", "end_date",
#             "current_joining_date", "experience",
#             "portfolio_link", "github_link", "linkedin_link"
#         ]
#         widgets = {
#             "start_date": forms.DateInput(attrs={"type": "date"}),
#             "end_date": forms.DateInput(attrs={"type": "date"}),
#             "current_joining_date": forms.DateInput(attrs={"type": "date"}),
#         }


# # class LoginForm(AuthenticationForm):
# #     role = forms.ChoiceField(choices=CustomUser.ROLE_CHOICES)

# class LoginForm(AuthenticationForm):
#     username = forms.EmailField(
#         label="Email",
#         widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email'})
#     )
#     role = forms.ChoiceField(
#         choices=CustomUser.ROLE_CHOICES,
#         widget=forms.Select(attrs={'class': 'form-select'})
#     )
    
# class OTPForm(forms.Form):
#     otp = forms.CharField(
#         max_length=6,
#         min_length=6,
#         widget=forms.TextInput(attrs={'placeholder': 'Enter 6-digit OTP'})
#     )


from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser
from Student.models import StudentProfile
from Teacher.models import TeacherProfile


# -------------------- STUDENT FORMS --------------------
class StudentRegistrationForm(UserCreationForm):
    email = forms.EmailField(max_length=254, help_text='Required. Enter a valid email address.')

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('email', 'profile_picture')


class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = ('address', 'mobile_number', 'educational_background', 'passing_year', 'bio')


# -------------------- TEACHER FORMS --------------------
class TeacherRegistrationForm(UserCreationForm):
    email = forms.EmailField(max_length=254, help_text='Required. Enter a valid email address.')

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('email', 'profile_picture')


# ✅ NEW — for registration step (personal + education)
class TeacherProfileRegistrationForm(forms.ModelForm):
    class Meta:
        model = TeacherProfile
        fields = [
            "full_name", "gender", "mobile_number", "date_of_birth",
            "country", "state", "address", "bio",
            "qualification_type", "institution_name", "passing_year", "currently_studying"
        ]
        widgets = {
            "date_of_birth": forms.DateInput(attrs={"type": "date"}),
        }


# ✅ NEW — for profile update step (experience + links)
class TeacherProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = TeacherProfile
        fields = [
            "bio", "prev_workplace", "designation", "start_date", "end_date",
            "current_joining_date", "experience",
            "portfolio_link", "github_link", "linkedin_link",
        ]
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
            "current_joining_date": forms.DateInput(attrs={"type": "date"}),
        }


# -------------------- AUTH FORMS --------------------
class LoginForm(AuthenticationForm):
    username = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email'})
    )
    role = forms.ChoiceField(
        choices=CustomUser.ROLE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )


class OTPForm(forms.Form):
    otp = forms.CharField(
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={'placeholder': 'Enter 6-digit OTP'})
    )
