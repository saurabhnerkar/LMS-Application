from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView, CreateView, UpdateView,DeleteView
from django.utils import timezone
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.views import PasswordChangeView
from Courses.models import Course
from Student.models import Enrollment,StudentProfile,AssignmentSubmission,Feedback,Notification, QuizSubmission, QuizAnswer
from django.views import View
from django.contrib import messages
from Teacher.models import Note, TeacherAssignment, Quiz, Question, Choice
from .forms import StudentProfileForm, EnrollmentForm, AssignmentSubmissionForm, FeedbackForm
from django.db import transaction
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy

@login_required
def student_dashboard(request):
    profile, _ = StudentProfile.objects.get_or_create(user=request.user)
    enrollments = Enrollment.objects.filter(student=profile)

    my_courses = [
        {
            "title": e.course.title,
            "id": e.course.id,
            "enrolled_on": e.enrollment_date,  # FIXED
            "image": e.course.image if hasattr(e.course, 'image') else None
        }
        for e in enrollments
    ]

    notifications = request.user.notifications.filter(is_read=False).order_by('-created_at')[:5]
    notifications_count = notifications.count()

    context = {
        "profile": profile,
        "my_courses": my_courses,  # IMPORTANT
        "notifications": notifications,
        "notifications_count": notifications_count,
        "total_courses": Course.objects.count(),
        "enrolled_courses": enrollments.count(),
        
    }

    return render(request, "student/student_dashboard.html", context)

class StudentProfileDetailView(DetailView):
    model = StudentProfile
    template_name = "student/student_profile.html"

    def get_object(self):
        return get_object_or_404(StudentProfile, user=self.request.user)

class StudentProfileCreateView(CreateView):
    model = StudentProfile
    fields = ["address", "mobile_number", "educational_background", "passing_year", "bio"]
    template_name = "student/studentprofile_form.html"
    success_url = reverse_lazy("student:studentprofile_detail")

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, "Profile created successfully.")
        return super().form_valid(form)

class StudentProfileUpdateView(UpdateView):
    model = StudentProfile
    form_class = StudentProfileForm
    template_name = "student/studentprofile_form.html"
    success_url = reverse_lazy("student:studentprofile_detail")

    def get_object(self):
        return get_object_or_404(StudentProfile, user=self.request.user)

    def get_initial(self):
        initial = super().get_initial()
        user = self.request.user
        
        initial["first_name"] = user.first_name
        initial["last_name"] = user.last_name
        initial["email"] = user.email
        initial["username"] = user.username
        
        return initial

    def form_valid(self, form):
        # Save StudentProfile data
        profile = form.save()

        # Save CustomUser data also
        user = self.request.user
        user.first_name = form.cleaned_data["first_name"]
        user.last_name = form.cleaned_data["last_name"]
        user.email = form.cleaned_data["email"]
        user.username = form.cleaned_data["username"]
        user.save()

        messages.success(self.request, "Profile updated successfully.")
        return super().form_valid(form)


# class CourseListView(ListView):
#     model = Course
#     template_name = "student/course_list.html"
#     context_object_name = "courses"

# class CourseDetailView(DetailView):
#     model = Course
#     template_name = "student/course_detail.html"
#     context_object_name = "course"

from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.views.generic.edit import CreateView
from django.views import View


class EnrollCourseView(View):
    template_name = "student/enroll_confirm.html"

    def get(self, request, *args, **kwargs):
        course = get_object_or_404(Course, pk=kwargs['pk'])
        context = {'course': course}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        course = get_object_or_404(Course, pk=kwargs['pk'])
        student_profile = get_object_or_404(StudentProfile, user=request.user)

        if Enrollment.objects.filter(student=student_profile, course=course).exists():
            messages.warning(request, "You are already enrolled in this course.")
            return redirect("student:enrollment_list")

        # Redirect to payment page where enrollment creation and payment happens
        return redirect('dummy_payment', pk=course.pk)
    

class EnrollmentListView(ListView):
    model = Enrollment
    template_name = "student/enrollment_list.html"
    context_object_name = "enrollments"

    def get_queryset(self):
        student_profile = get_object_or_404(StudentProfile, user=self.request.user)
        return Enrollment.objects.filter(student=student_profile)

class EnrollmentDetailView(DetailView):
    model = Enrollment
    template_name = "student/enrollment_detail.html"
    context_object_name = "enrollment"

    def get_queryset(self):
        student_profile = get_object_or_404(StudentProfile, user=self.request.user)
        return Enrollment.objects.filter(student=student_profile)
    
class EnrollmentDeleteView(DeleteView):
    model = Enrollment
    success_url = reverse_lazy('student:enrollment_list')  # Redirect to list after delete
    template_name = "student/enrollment_confirm_delete.html"
    
    def get_queryset(self):
        try:
           student_profile = StudentProfile.objects.get(user=self.request.user)
        except StudentProfile.DoesNotExist:
        # Handle the missing profile gracefully, e.g.,
             return Enrollment.objects.none()  # empty queryset
        return Enrollment.objects.filter(student=student_profile)



class AssignmentSubmissionCreateView(CreateView):
    model = AssignmentSubmission
    fields = ["file"]
    template_name = "student/assignment_submission_form.html"

    def form_valid(self, form):
        enrollment = get_object_or_404(Enrollment, id=self.kwargs["enrollment_id"])
        form.instance.enrollment = enrollment
        messages.success(self.request, "Assignment submitted successfully.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("student:submission_list")

class AssignmentSubmissionListView(ListView):
    model = AssignmentSubmission
    template_name = "student/assignment_submission_list.html"
    context_object_name = "submissions"

    def get_queryset(self):
        student_profile = get_object_or_404(StudentProfile, user=self.request.user)
        course_id = self.kwargs.get('course_id')
        return AssignmentSubmission.objects.filter(
            enrollment__student=student_profile,
            enrollment__course__id=course_id
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course_id = self.kwargs.get('course_id')
        context["course"] = get_object_or_404(Course, id=course_id)
        return context

class AssignmentSubmissionDetailView(DetailView):
    model = AssignmentSubmission
    template_name = "student/assignment_submission_detail.html"
    context_object_name = "submission"

    def get_queryset(self):
        student_profile = get_object_or_404(StudentProfile, user=self.request.user)
        return AssignmentSubmission.objects.filter(enrollment__student=student_profile)

# class FeedbackCreateView(CreateView):
#     model = Feedback
#     fields = ["rating", "feedback_text"]
#     template_name = "student/feedback_form.html"

#     def form_valid(self, form):
#         course = get_object_or_404(Course, pk=self.kwargs["course_id"])
#         student_profile = get_object_or_404(StudentProfile, user=self.request.user)
#         form.instance.course = course
#         form.instance.student = student_profile
#         messages.success(self.request, "Feedback submitted successfully.")
#         return super().form_valid(form)

#     def get_success_url(self):
#         return reverse_lazy("student:feedback_list")

# class FeedbackListView(ListView):
#     model = Feedback
#     template_name = "student/feedback_list.html"
#     context_object_name = "feedbacks"

#     def get_queryset(self):
#         student_profile = get_object_or_404(StudentProfile, user=self.request.user)
#         return Feedback.objects.filter(student=student_profile)



def feedback_course_list(request):
    student_profile = get_object_or_404(StudentProfile, user=request.user)

    enrollments = Enrollment.objects.filter(student=student_profile)
    old_feedbacks = Feedback.objects.filter(student=student_profile)

    return render(request, "student/feedback_course_list.html", {
        "enrollments": enrollments,
        "old_feedbacks": old_feedbacks,
    })

class FeedbackCreateView(View):
    def get(self, request, course_id):
        course = get_object_or_404(Course, pk=course_id)
        return render(request, "student/feedback_form.html", {"course": course})

    def post(self, request, course_id):
        course = get_object_or_404(Course, pk=course_id)
        student_profile = get_object_or_404(StudentProfile, user=request.user)

        Feedback.objects.create(
            course=course,
            student=student_profile,

            # New rating fields
            relevance_rating=request.POST.get("relevance_rating"),
            trainer_knowledge_rating=request.POST.get("trainer_knowledge_rating"),
            overall_satisfaction_rating=request.POST.get("overall_satisfaction_rating"),

            # New MCQ fields
            material_easy=request.POST.get("material_easy"),
            duration_appropriate=request.POST.get("duration_appropriate"),
            achieved_objective=request.POST.get("achieved_objective"),
            recommend_trainer=request.POST.get("recommend_trainer"),

            # Text suggestion
            improvement_suggestions=request.POST.get("improvement_suggestions")
        )

        messages.success(request, "Feedback submitted successfully.")
        return redirect("student:feedback_course_list")




class FeedbackListView(ListView):
    model = Feedback
    template_name = "student/feedback_list.html" 
    context_object_name = "feedbacks"

    def get_queryset(self):
        student_profile = get_object_or_404(StudentProfile, user=self.request.user)
        return Feedback.objects.filter(student=student_profile)



class FeedbackUpdateView(UpdateView):
    model = Feedback
    template_name = "student/feedback_form_edit.html"
    fields = [
        "relevance_rating",
        "material_easy",
        "trainer_knowledge_rating",
        "duration_appropriate",
        "achieved_objective",
        "recommend_trainer",
        "overall_satisfaction_rating",
        "improvement_suggestions",
    ]

    def get_success_url(self):
        messages.success(self.request, "Feedback updated successfully.")
        return reverse_lazy("student:feedback_list")

@login_required
def mark_all_as_read(request):
    request.user.notifications.update(is_read=True)
    return redirect('student:student_dashboard')

class StudentChangePasswordView(PasswordChangeView):
    template_name = 'student/change_password.html'
    success_url = reverse_lazy('student:student_dashboard')
    def form_valid(self, form):
        messages.success(self.request, "Your password was changed successfully.")
        return super().form_valid(form)
    
def course_list(request):
    print("DEBUG: course_list view called")
    courses = Course.objects.all()
    print("Courses:", courses)
    return render(request, 'student/course_list.html', {'courses': courses})

def course_detail(request, pk):
    course = get_object_or_404(Course, pk=pk)

    # Check if the current user is an enrolled student for this course
    is_enrolled = False
    if request.user.is_authenticated:
        # ensure StudentProfile exists and belongs to this user
        try:
            student_profile = StudentProfile.objects.get(user=request.user)
            is_enrolled = Enrollment.objects.filter(student=student_profile, course=course).exists()
        except StudentProfile.DoesNotExist:
            is_enrolled = False

    notes = assignments = quizzes = None
    if is_enrolled:
        # use the related_name on the teacher models:
        # Note.related_name = 'notes', TeacherAssignment.related_name = 'assignments', Quiz.related_name = 'quizzes'
        notes = course.notes.all()
        assignments = course.assignments.all()
        quizzes = course.quizzes.all()

    context = {
        'course': course,
        'is_enrolled': is_enrolled,
        'notes': notes,
        'assignments': assignments,
        'quizzes': quizzes,
    }
    return render(request, 'student/course_detail.html', context)


@login_required
def dummy_payment(request, pk):
    try:
        course = get_object_or_404(Course, pk=pk)
        student_profile = get_object_or_404(StudentProfile, user=request.user)

        if Enrollment.objects.filter(student=student_profile, course=course).exists():
            messages.warning(request, "You are already enrolled in this course.")
            return redirect('student:enrollment_list')

        if request.method == "POST":
            enrollment = Enrollment.objects.create(
                student=student_profile,
                course=course,
                payment_completed=True,
                enrollment_date=timezone.now()
            )
            send_mail(
                subject="Course Enrollment Confirmation",
                message=f"Dear {request.user.get_full_name() or request.user.username},\n\nYou have successfully enrolled in '{course.title}'.",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[request.user.email],
            )
        
            teacher_email = course.teacher.user.email  
            send_mail(
                subject="New Course Enrollment",
                message=f"Course '{course.title}' has been enrolled by {request.user.get_full_name() or request.user.username} ({request.user.email}).",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[teacher_email],
            )

            messages.success(request, f"Successfully enrolled in {course.title}")
            return redirect('student:student_dashboard')
        context = {
            'course': course,
            'student': student_profile,
            'amount': course.price if hasattr(course, 'price') else 0
        }
        return render(request, 'student/dummy_payment.html', context)

    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('student:course_list')
 
@login_required
def assigned_notes(request, course_id):
    student_profile = StudentProfile.objects.get(user=request.user)
    course = Course.objects.get(id=course_id)
    
    # Verify the student is enrolled in this course
    is_enrolled = Enrollment.objects.filter(student=student_profile, course=course).exists()
    if not is_enrolled:
        messages.error(request, "You are not enrolled in this course.")
        return redirect('student:course_list')
    
    # Fetch notes for this course
    notes = Note.objects.filter(course=course)
    return render(request, 'student/assigned_notes.html', {'notes': notes, 'course': course})

def view_note(request, course_id, note_id):
    student_profile = get_object_or_404(StudentProfile, user=request.user)
    course = get_object_or_404(Course, id=course_id)
    note = get_object_or_404(Note, id=note_id, course=course)

    # Optional: make sure student is enrolled
    if not Enrollment.objects.filter(student=student_profile, course=course).exists():
        messages.error(request, "You are not enrolled in this course.")
        return redirect('student:course_list')

    return render(request, 'student/view_notes.html', {'note': note, 'course': course})

@login_required
def assigned_assignments(request, course_id):
    student_profile = get_object_or_404(StudentProfile, user=request.user)
    course = get_object_or_404(Course, id=course_id)

    # Verify enrollment
    enrollment = Enrollment.objects.filter(student=student_profile, course=course).first()
    print("Enrollment:", enrollment)
    if not enrollment:
        messages.error(request, "You are not enrolled in this course.")
        return redirect('student:course_list')

    # Fetch assignments for this course
    assignments = TeacherAssignment.objects.filter(course=course)
    print("Assignments:", assignments)
    
    # Get IDs of assignments this student has submitted
    submitted_ids = AssignmentSubmission.objects.filter(
        enrollment=enrollment
    ).values_list('assignment_id', flat=True)

    return render(request, 'student/assignment_submission_list.html', {
        'assignments': assignments,
        'course': course,
        'submitted_ids': submitted_ids,
        'enrollment_id': enrollment.id,
    })
    
@login_required
def view_assignment(request, course_id, assignment_id):
    student_profile = get_object_or_404(StudentProfile, user=request.user)
    course = get_object_or_404(Course, id=course_id)
    assignment = get_object_or_404(TeacherAssignment, id=assignment_id, course=course)

    # Ensure the student is enrolled
    enrollment = Enrollment.objects.filter(student=student_profile, course=course).first()
    if not enrollment:
        messages.error(request, "You are not enrolled in this course.")
        return redirect('student:course_list')

    # Check if submission exists
    existing_submission = AssignmentSubmission.objects.filter(
        enrollment=enrollment,
        assignment=assignment
    ).first()

    context = {
        'assignment': assignment,
        'course': course,
        'existing_submission': existing_submission,
        'grade': existing_submission.grade if existing_submission else None,
        'remarks': existing_submission.remarks if existing_submission else None,
    }

    return render(request, 'student/view_assignment.html', context)

@login_required
def submit_assignment(request, course_id, assignment_id):
    from Student.notify import notify_teacher   # <-- ADD THIS

    student_profile = get_object_or_404(StudentProfile, user=request.user)
    course = get_object_or_404(Course, id=course_id)
    assignment = get_object_or_404(TeacherAssignment, id=assignment_id, course=course)
    enrollment = get_object_or_404(Enrollment, student=student_profile, course=course)

    existing_submission = AssignmentSubmission.objects.filter(
        enrollment=enrollment,
        assignment=assignment
    ).first()

    if request.method == "POST":
        if existing_submission:
            messages.warning(request, "You have already submitted this assignment.")
        else:
            file = request.FILES.get("file")
            if not file:
                messages.error(request, "Please select a file before submitting.")
            else:
                # Create submission
                AssignmentSubmission.objects.create(
                    enrollment=enrollment,
                    assignment=assignment,
                    file=file
                )

                # 🔔 Notify Teacher
                notify_teacher(
                    course,
                    f"{request.user.get_full_name() or request.user.username} uploaded assignment '{assignment.title}' for course '{course.title}'."
                )

                messages.success(request, "Assignment submitted successfully!")
                return redirect('student:assigned_assignments', course_id=course.id)

    return redirect('student:view_assignment', course_id=course.id, assignment_id=assignment.id)

@login_required
def edit_submission(request, course_id, assignment_id):
    student_profile = get_object_or_404(StudentProfile, user=request.user)
    course = get_object_or_404(Course, id=course_id)
    assignment = get_object_or_404(TeacherAssignment, id=assignment_id, course=course)
    enrollment = get_object_or_404(Enrollment, student=student_profile, course=course)

    submission = get_object_or_404(AssignmentSubmission, enrollment=enrollment, assignment=assignment)

    if request.method == "POST":
        file = request.FILES.get("file")
        if file:
            submission.file = file
            submission.submitted_on = timezone.now()
            submission.save()
            messages.success(request, "Assignment updated successfully.")
            return redirect('student:view_assignment', course_id=course.id, assignment_id=assignment.id)
        else:
            messages.error(request, "Please choose a file to upload.")
    
    return render(request, 'student/edit_submission.html', {
        'assignment': assignment,
        'course': course,
        'submission': submission,
    })

@login_required
def delete_submission(request, course_id, assignment_id):
    student_profile = get_object_or_404(StudentProfile, user=request.user)
    course = get_object_or_404(Course, id=course_id)
    assignment = get_object_or_404(TeacherAssignment, id=assignment_id, course=course)
    enrollment = get_object_or_404(Enrollment, student=student_profile, course=course)

    submission = get_object_or_404(AssignmentSubmission, enrollment=enrollment, assignment=assignment)

    if request.method == "POST":
        submission.delete()
        messages.success(request, "Submission deleted successfully.")
        return redirect('student:view_assignment', course_id=course.id, assignment_id=assignment.id)

    return render(request, 'student/delete_submission_confirm.html', {
        'assignment': assignment,
        'course': course,
        'submission': submission,
    })
    
@login_required
def student_quiz_list(request, course_id):
    student = request.user.student_profile

    # Ensure the student is enrolled in this course
    try:
        enrollment = Enrollment.objects.get(student=student, course_id=course_id)
    except Enrollment.DoesNotExist:
        messages.error(request, "You are not enrolled in this course.")
        return redirect('student:course_list')

    # Fetch quizzes for this specific course only
    quizzes = Quiz.objects.filter(course_id=course_id)
    course = enrollment.course
    now = timezone.localtime(timezone.now())
    return render(request, 'student/assigned_quizzes.html', {
        'quizzes': quizzes,
        'now': now,
        'course': course
    })
    
@login_required
def take_quiz(request, course_id, quiz_id):
    from Student.notify import notify_teacher   # <-- ADD THIS IMPORT

    quiz = get_object_or_404(Quiz, id=quiz_id)
    course = get_object_or_404(Course, id=course_id)
    student = request.user.student_profile
    enrollment = Enrollment.objects.filter(student=student, course=quiz.course).first()

    if not enrollment:
        return render(request, 'student/not_enrolled.html')

    now = timezone.now()
    if quiz.start_time and quiz.end_time and not (quiz.start_time <= now <= quiz.end_time):
        return render(request, 'student/quiz_disabled.html', {'quiz': quiz})

    # Avoid duplicate submission
    existing_submission = QuizSubmission.objects.filter(enrollment=enrollment, quiz=quiz).first()
    if existing_submission and existing_submission.answers.exists():
        return redirect('student:quiz_result', course_id=course.id, quiz_id=quiz.id)

    questions = quiz.questions.all()

    if request.method == 'POST':
        score = 0
        with transaction.atomic():
            submission = QuizSubmission.objects.create(enrollment=enrollment, quiz=quiz, score=0)
            for question in questions:
                selected_option_id = request.POST.get(str(question.id))
                selected_choice = None
                is_correct = False

                if selected_option_id:
                    selected_choice = Choice.objects.filter(id=selected_option_id).first()
                    if selected_choice and selected_choice.is_correct:
                        is_correct = True
                        score += 1

                QuizAnswer.objects.create(
                    submission=submission,
                    question=question,
                    selected_option=selected_choice,
                    is_correct=is_correct
                )

            submission.score = score
            submission.save()

            
            notify_teacher(
                quiz.course,
                f"{request.user.get_full_name() or request.user.username} completed quiz '{quiz.title}' with score {score}."
            )

        return redirect('student:quiz_result', course_id=course.id, quiz_id=quiz.id)

    return render(request, 'student/quiz_take.html', {
        'quiz': quiz,
        'questions': questions,
    })


@login_required
def quiz_result(request, course_id, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    course = get_object_or_404(Course, id=course_id)
    student = request.user.student_profile

    # Check enrollment
    enrollment = Enrollment.objects.filter(student=student, course=course).first()
    if not enrollment:
        return render(request, 'student/not_enrolled.html')

    # Get submission / attempt
    submission = QuizSubmission.objects.filter(enrollment=enrollment, quiz=quiz).first()
    if not submission:
        messages.error(request, "You haven't attempted this quiz yet.")
        return redirect('student:student_quiz_list', course_id=course.id)

    # Build question results
    question_results = []
    correct_answers = 0
    total_questions = quiz.questions.count()
    total_marks = quiz.total_marks or 0

    for answer in submission.answers.all():
        # Get correct choice
        correct_choice = answer.question.choices.filter(is_correct=True).first()
        is_correct = answer.selected_option == correct_choice

        # Count correct answers
        if is_correct:
            correct_answers += 1

        question_results.append({
            'question': answer.question,
            'selected_option': answer.selected_option.text if answer.selected_option else None,
            'correct_option': correct_choice.text if correct_choice else None,
            'is_correct': is_correct,
        })

    # Calculate score (for example: marks per question)
    marks_per_question = total_marks / total_questions if total_questions > 0 else 0
    score = round(correct_answers * marks_per_question)

    return render(request, 'student/quiz_result.html', {
        'quiz': quiz,
        'submission': submission,
        'question_results': question_results,
        'score': score,
        'correct_answers': correct_answers,
        'total_questions': total_questions,
        'attempt_date': submission.submitted_on,
    })


