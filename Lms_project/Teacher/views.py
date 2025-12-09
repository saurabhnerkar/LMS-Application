from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import TeacherProfile, Note, TeacherAssignment, Quiz
from .forms import *
from Student.models import Enrollment, AssignmentSubmission, Feedback, StudentProfile
from Courses.models import Course
# <<<<<<< Updated upstream
from django.forms import modelformset_factory
from django.http import HttpResponse
from openpyxl import Workbook
# from openpyxl.writer.excel import save_virtual_workbook
from io import BytesIO
from openpyxl import Workbook

def teacher_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "Please login first.")
            return redirect("accounts:login")
        if request.user.role != "teacher":
            messages.error(request, "Access denied. Teacher account required.")
            return redirect("home")
        return view_func(request, *args, **kwargs)
    return _wrapped_view

@login_required
def teacher_dashboard(request):
    try:
        teacher_profile = TeacherProfile.objects.get(user=request.user)
    except TeacherProfile.DoesNotExist:
        teacher_profile = None

    if not teacher_profile:
        messages.warning(request, "Your teacher profile is not yet created. Please contact admin.")
        return render(request, "teacher/teacher_dashboard.html", {
            "teacher": None,
            "courses": [],
            "notifications": [],
            "notifications_count": 0
        })

    # Fetch all courses assigned to this teacher
    assigned_courses = teacher_profile.courses.all()


    course_data = []
    for course in assigned_courses:
        student_count = course.enrollments.count()     
        course_data.append({
            "course_name": course.title,
            "student_count": student_count,
        })

    # Notifications
    notifications = request.user.notifications.filter(is_read=False).order_by('-created_at')[:10]
    notifications_count = notifications.count()

    context = {
        "teacher": teacher_profile,
        "course_data": course_data,
        "course_count": assigned_courses.count(),
        "total_learners": sum(c["student_count"] for c in course_data),

        # Notifications
        "notifications": notifications,
        "notifications_count": notifications_count,
    }

    return render(request, "teacher/teacher_dashboard.html", context)

@login_required
def teacher_mark_all_as_read(request):
    request.user.notifications.update(is_read=True)
    return redirect(request.META.get('HTTP_REFERER', 'teacher:teacher_dashboard'))




@login_required
@teacher_required
def update_profile(request):
    teacher_profile, created = TeacherProfile.objects.get_or_create(user=request.user)

    # Pre-fill user fields and profile fields
    if request.method == "POST":
        form = TeacherProfileForm(request.POST, instance=teacher_profile)

        if form.is_valid():
            # Save profile data
            form.save()

            # Save user data
            user = request.user
            user.first_name = form.cleaned_data.get("first_name")
            user.last_name  = form.cleaned_data.get("last_name")
            user.email      = form.cleaned_data.get("email")
            user.username   = form.cleaned_data.get("username")
            user.save()

            messages.success(request, "Profile updated successfully.")
            return redirect("teacher:teacher_dashboard")

    else:
        form = TeacherProfileForm(instance=teacher_profile)
        # Pre-fill user fields
        form.fields["first_name"].initial = request.user.first_name
        form.fields["last_name"].initial = request.user.last_name
        form.fields["email"].initial = request.user.email
        form.fields["username"].initial = request.user.username

    return render(request, "teacher/update_profile.html", {"form": form})

@login_required
@teacher_required
def view_courses(request):
    teacher_profile = get_object_or_404(TeacherProfile, user=request.user)
    courses = Course.objects.filter(teacher=teacher_profile)
    return render(request, "teacher/view_courses.html", {"courses": courses})

from Student.notify import notify_students

@login_required
@teacher_required
def add_note(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if request.method == "POST":
        form = NoteForm(request.POST, request.FILES)
        if form.is_valid():
            note = form.save(commit=False)
            note.course = course
            note.teacher = request.user
            note.save()
            notify_students(course, f"New note uploaded for {course.title}: {note.title}")
            messages.success(request, "Note uploaded successfully!")
            return redirect("teacher:course_detail", course_id=course.id)
    else:
        form = NoteForm()
    return render(request, "teacher/add_note.html", {"form": form, "course": course})

@login_required
def add_assignment(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    if request.method == "POST":
        form = TeacherAssignmentForm(request.POST, request.FILES)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.teacher = request.user
            assignment.course = course
            assignment.save()
            notify_students(
                course,
                f"New assignment posted in {course.title}: {assignment.title}"
            )
            messages.success(request, "Assignment created successfully!")
            return redirect("teacher:course_detail", course_id=course.id)
    else:
        form = TeacherAssignmentForm()
    return render(request, "teacher/add_assignment.html", {"form": form, "course": course})

@login_required
def course_detail(request, course_id):
    teacher_profile = get_object_or_404(TeacherProfile, user=request.user)
    course = get_object_or_404(Course, id=course_id, teacher=teacher_profile)
    notes = Note.objects.filter(course=course)
    assignments = TeacherAssignment.objects.filter(course=course)
    # Count how many students are enrolled in this course
    student_count = Enrollment.objects.filter(course=course).count()
    context = {
        "course": course,
        "notes": notes,
        "assignments": assignments,
        "student_count": student_count,  # pass to template
    }
    return render(request, "teacher/course_detail.html", context)

@login_required
def view_profile(request):
    """
    Display the teacher's profile details.
    """
    teacher_profile = get_object_or_404(TeacherProfile, user=request.user)

    context = {
        "teacher": teacher_profile,
    }
    return render(request, "teacher/view_profile.html", context)

@login_required
def course_assignments(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    assignments = TeacherAssignment.objects.filter(course=course)
    
    assignments_data = []
    total_students = Enrollment.objects.filter(course=course).count()

    for assignment in assignments:
        # Count student submissions for this assignment
        submitted_count = AssignmentSubmission.objects.filter(assignment=assignment).count()
        not_submitted_count = max(total_students - submitted_count, 0)
        submission_percentage = (submitted_count / total_students * 100) if total_students > 0 else 0

        assignments_data.append({
            'assignment': assignment,
            'total_students': total_students,
            'submitted_count': submitted_count,
            'not_submitted_count': not_submitted_count,
            'submission_percentage': round(submission_percentage, 1)
        })

    context = {
        'course': course,
        'assignments_data': assignments_data
    }
    return render(request, 'teacher/course_assignments_list.html', context)

@login_required
@teacher_required
def quiz_list(request, course_id=None):
    """List quizzes (all or for a course)."""
    if course_id:
        course = get_object_or_404(Course, id=course_id)
        quizzes = Quiz.objects.filter(course=course)
        context = {'quizzes': quizzes, 'course': course}
    else:
        quizzes = Quiz.objects.filter(teacher=request.user)
        context = {'quizzes': quizzes, 'course': None}
    return render(request, 'teacher/quiz_list.html', context)

@login_required
def create_quiz_with_questions(request):
    QuestionFormSet = inlineformset_factory(
        Quiz, Question,
        form=QuestionForm,
        extra=1,
        can_delete=False
    )

    if request.method == 'POST':
        quiz_form = QuizForm(request.POST)
        question_formset = QuestionFormSet(request.POST)

        if quiz_form.is_valid() and question_formset.is_valid():
            quiz = quiz_form.save(commit=False)
            quiz.teacher = request.user
            quiz.save()

            questions = question_formset.save(commit=False)
            for q in questions:
                q.quiz = quiz
                q.save()

            messages.success(request, "Quiz created! Now add options for each question.")
            return redirect('add_options', quiz_id=quiz.id)
    else:
        quiz_form = QuizForm()
        question_formset = QuestionFormSet()

    return render(request, 'teacher/create_quiz.html', {
        'quiz_form': quiz_form,
        'question_formset': question_formset
    })
@login_required
@teacher_required
def create_quiz(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    if request.method == 'POST':
        quiz_form = QuizForm(request.POST)
        if quiz_form.is_valid():
            quiz = quiz_form.save(commit=False)
            quiz.teacher = request.user
            quiz.course = course
            quiz.save()

    
            from Student.notify import notify_students
            notify_students(
                course,
                f"New quiz published in {course.title}: {quiz.title}"
            )

            # Save questions
            question_texts = request.POST.getlist('question_text[]')
            question_marks = request.POST.getlist('question_marks[]')

            for i, text in enumerate(question_texts):
                marks = question_marks[i] if i < len(question_marks) else 1
                question = Question.objects.create(
                    quiz=quiz,
                    text=text,
                    marks=marks
                )

                option_texts = request.POST.getlist(f'option_text_{i}[]')
                correct_options = request.POST.getlist(f'correct_option_{i}[]')

                for j, opt_text in enumerate(option_texts):
                    is_correct = str(j) in correct_options
                    Choice.objects.create(
                        question=question,
                        text=opt_text,
                        is_correct=is_correct
                    )

            messages.success(request, f"Quiz '{quiz.title}' created successfully!")
            return redirect('teacher:course_quizzes', course_id=course.id)

        else:
            messages.error(request, "Please fix the errors in the quiz form.")

    else:
        quiz_form = QuizForm()

    return render(request, 'teacher/create_quiz.html', {
        'quiz_form': quiz_form,
        'course': course
    })


@login_required
def add_quiz(request, course_id):
    """Handles quiz + question creation in one page."""
    course = get_object_or_404(Course, id=course_id)
    QuestionFormSet = modelformset_factory(Question, form=QuestionForm, extra=3)

    if request.method == 'POST':
        quiz_form = QuizForm(request.POST)
        question_formset = QuestionFormSet(request.POST)
        if quiz_form.is_valid() and question_formset.is_valid():
            quiz = quiz_form.save(commit=False)
            quiz.course = course
            quiz.teacher = request.user
            quiz.save()

            # Save questions linked to this quiz
            questions = question_formset.save(commit=False)
            for question in questions:
                question.quiz = quiz
                question.save()

            messages.success(request, "Quiz and questions created successfully!")
            return redirect('teacher:quiz_list', course_id=course.id)
    else:
        quiz_form = QuizForm()
        question_formset = QuestionFormSet()

    return render(request, 'teacher/add_quiz.html', {
        'quiz_form': quiz_form,
        'question_formset': question_formset,
        'course': course,
    })
    
@login_required
@teacher_required
def add_question(request, course_id, quiz_id):
    course = get_object_or_404(Course, id=course_id)
    quiz = get_object_or_404(Quiz, id=quiz_id)
    form = QuestionForm(request.POST or None)
    formset = ChoiceFormSet(request.POST or None)
    questions = Question.objects.filter(quiz=quiz)

    if request.method == 'POST':
        if form.is_valid() and formset.is_valid():
            question = form.save(commit=False)
            question.quiz = quiz
            question.save()
            formset.instance = question
            formset.save()

            messages.success(request, "Question added successfully!")
            return redirect('teacher:add_question', course_id=course.id, quiz_id=quiz.id)
        else:
            print("DEBUG: Question form errors:", form.errors)
            print("DEBUG: Choice formset errors:", formset.errors)
            messages.error(request, "There was an error adding the question. Check server console for details.")

    # ✅ Render form for GET or invalid POST
    return render(request, 'teacher/add_question.html', {
        'course': course,
        'quiz': quiz,
        'form': form,
        'formset': formset, 
        'questions': questions,
    })


@login_required
@teacher_required
def delete_question(request, course_id, quiz_id, question_id):
    """
    ✅ Delete a question from a quiz.
    """
    quiz = get_object_or_404(Quiz, id=quiz_id)
    question = get_object_or_404(Question, id=question_id, quiz=quiz)
    if request.method == 'POST':
        question.delete()
        messages.success(request, "Question deleted successfully!")
        return redirect('teacher:add_question', course_id=course_id, quiz_id=quiz_id)

@login_required
@teacher_required
def edit_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    if quiz.teacher != request.user:
        messages.error(request, 'Access denied.')
        return redirect('teacher:quiz_list')
    if request.method == 'POST':
        form = QuizForm(request.POST, instance=quiz)
        if form.is_valid():
            form.save()
            messages.success(request, 'Quiz updated.')
            return redirect('teacher:course_quizzes', course_id=quiz.course.id)
    else:
        form = QuizForm(instance=quiz)
    return render(request, 'teacher/edit_quiz.html', {'form': form, 'quiz': quiz, 'course': quiz.course})


@login_required
@teacher_required
def delete_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    if quiz.teacher != request.user:
        messages.error(request, 'Access denied.')
        return redirect('teacher:quiz_list')
    if request.method == 'POST':
        course_id = quiz.course.id
        quiz.delete()
        messages.success(request, 'Quiz deleted.')
        return redirect('teacher:course_quizzes', course_id=course_id)
    return render(request, 'teacher/delete_quiz_confirm.html', {'quiz': quiz, 'course': quiz.course})

@login_required
@teacher_required
def quiz_detail(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    course = quiz.course

    total_students = Enrollment.objects.filter(course=course).count()
    attempted_students = QuizSubmission.objects.filter(quiz=quiz)
    attempted_ids = attempted_students.values_list('enrollment__student__id', flat=True)
    not_attempted_students = StudentProfile.objects.filter(
    id__in=Enrollment.objects.filter(course=course).values_list('student_id', flat=True)
).exclude(id__in=attempted_ids)

    submitted_count = attempted_students.count()
    not_submitted_count = not_attempted_students.count()
    attempted_percentage = (submitted_count / total_students * 100) if total_students else 0
    pending_percentage = (not_submitted_count / total_students * 100) if total_students else 0

    # Combine student + attempt data for table
    attempted_info = [
        {"student": attempt.enrollment.student, "attempt": attempt}
        for attempt in attempted_students
    ]

    context = {
        "quiz": quiz,
        "total_students": total_students,
        "attempted_students": attempted_students,
        "not_attempted_students": not_attempted_students,
        "attempted_percentage": attempted_percentage,
        "pending_percentage": pending_percentage,
        "attempted_info": attempted_info,
    }
    return render(request, "teacher/quiz_detail.html", context)

@login_required
def assignment_list(request, course_id=None):
    """List assignments for the logged-in teacher.

    If course_id is provided, filter assignments for that course.
    This view backs the URLs `assignments/` and `assignments/<course_id>/`.
    """
    if course_id:
        course = get_object_or_404(Course, id=course_id)
        assignments = TeacherAssignment.objects.filter(teacher=request.user, course=course)
        context = {
            'assignments': assignments,
            'course': course
        }
    else:
        assignments = TeacherAssignment.objects.filter(teacher=request.user)
        context = {
            'assignments': assignments,
            'course': None
        }
    return render(request, 'teacher/assignment_list.html', context)

@login_required
def assignment_submissions(request, assignment_id):
    assignment = get_object_or_404(TeacherAssignment, id=assignment_id)
    course = assignment.course

    # Get all enrollments for this course
    enrollments = Enrollment.objects.filter(course=course)
    enrolled_students = [e.student for e in enrollments]

    # Get all submissions for this specific assignment
    submissions = AssignmentSubmission.objects.filter(
        assignment=assignment
    ).select_related(
        'enrollment__student__user'
    ).order_by('enrollment__student__user__first_name')

    # Students who have submitted
    submitted_students = StudentProfile.objects.filter(
        id__in=submissions.values_list('enrollment__student__id', flat=True)
    )

    # Students who have not submitted
    not_submitted_students = [
        s for s in enrolled_students if s.id not in submitted_students.values_list('id', flat=True)
    ]

    # Build a mapping: student_id → latest submission
    submission_map = {}
    for sid in submitted_students.values_list('id', flat=True):
        sub_qs = AssignmentSubmission.objects.filter(
            enrollment__student__id=sid,
            enrollment__course__title=course.title
        ).order_by('-submitted_on')
        if sub_qs.exists():
            submission_map[sid] = sub_qs.first()

    # Prepare data for easy rendering
    submitted_info = [
        {
            'student': student,
            'submission': submission_map.get(student.id)
        }
        for student in submitted_students
    ]

    # Stats
    total_students = len(enrolled_students)
    submitted_count = submitted_students.count()
    not_submitted_count = len(not_submitted_students)
    submission_percentage = (submitted_count / total_students * 100) if total_students > 0 else 0
    pending_percentage = (not_submitted_count / total_students * 100) if total_students > 0 else 0

    context = {
        'assignment': assignment,
        'course': course,
        'submitted_students': submitted_students,
        'submitted_info': submitted_info,
        'not_submitted_students': not_submitted_students,
        'total_students': total_students,
        'submission_percentage': submission_percentage,
        'pending_percentage': pending_percentage,
    }
    return render(request, 'teacher/assignment_submissions.html', context)

@login_required
def edit_assignment(request, assignment_id):
    assignment = get_object_or_404(TeacherAssignment, id=assignment_id, teacher=request.user)
    
    if request.method == "POST":
        form = TeacherAssignmentForm(request.POST, request.FILES, instance=assignment)
        if form.is_valid():
            form.save()
            messages.success(request, "Assignment updated successfully!")
            return redirect('teacher:course_assignments_list', course_id=assignment.course.id)
    else:
        form = TeacherAssignmentForm(instance=assignment)
    
    return render(request, 'teacher/edit_assignment.html', {
        'form': form,
        'assignment': assignment,
        'course': assignment.course
    })

@login_required
@teacher_required
def delete_assignment(request, assignment_id):
    assignment = get_object_or_404(TeacherAssignment, id=assignment_id, teacher=request.user)
    course_id = assignment.course.id
    
    if request.method == "POST":
        assignment.delete()
        messages.success(request, "Assignment deleted successfully!")
        return redirect('teacher:course_assignments_list', course_id=course_id)
    
    return render(request, 'teacher/delete_assignment_confirm.html', {
        'assignment': assignment,
        'course': assignment.course
    })

@teacher_required
@login_required
def notes_list(request, course_id=None):
    # Get the teacher's profile
    teacher_profile = get_object_or_404(TeacherProfile, user=request.user)
    
    # Base query: notes by this teacher
    notes_query = Note.objects.filter(teacher=request.user)
    
    # If course_id is provided, filter by course
    if course_id:
        course = get_object_or_404(Course, id=course_id, teacher=teacher_profile)
        notes_query = notes_query.filter(course=course)
        context = {'notes': notes_query, 'course': course}
    else:
        context = {'notes': notes_query}
        
    return render(request, 'teacher/notes_list.html', context)

@login_required
@teacher_required
def view_note(request, note_id):
    # Get the note and verify it belongs to the teacher
    note = get_object_or_404(Note, id=note_id, teacher=request.user)
    return render(request, 'teacher/view_note.html', {'note': note})

@login_required
@teacher_required
def edit_note(request, note_id):
    note = get_object_or_404(Note, id=note_id, teacher=request.user)
    if request.method == "POST":
        form = NoteForm(request.POST, request.FILES, instance=note)
        if form.is_valid():
            form.save()
            messages.success(request, "Note updated successfully!")
            return redirect('teacher:view_note', note_id=note.id)
    else:
        form = NoteForm(instance=note)
    return render(request, 'teacher/edit_note.html', {'form': form, 'note': note})

@login_required
@teacher_required
def delete_note(request, note_id):
    note = get_object_or_404(Note, id=note_id, teacher=request.user)
    if request.method == "POST":
        course_id = note.course.id
        note.delete()
        messages.success(request, "Note deleted successfully!")
        return redirect('teacher:course_notes', course_id=course_id)
    return redirect('teacher:view_note', note_id=note_id)

@login_required
@teacher_required
def grade_submission(request, submission_id):
    submission = get_object_or_404(AssignmentSubmission, id=submission_id)
    assignment = submission.assignment
    course = assignment.course

    if request.method == "POST":
        form = GradeSubmissionForm(request.POST, instance=submission)
        if form.is_valid():
            form.save()
            messages.success(request, "Grade assigned successfully!")
            return redirect('teacher:assignment_submissions', assignment_id=assignment.id)
    else:
        form = GradeSubmissionForm(instance=submission)

    context = {
        'submission': submission,
        'assignment': assignment,
        'course': course,
        'form': form,
    }
    return render(request, 'teacher/grade_submission.html', context)

from django.shortcuts import render, get_object_or_404
from Student.models import Enrollment, QuizSubmission
from .models import Quiz

def quiz_submissions_list(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    enrollments = Enrollment.objects.filter(course=quiz.course)
    submitted = QuizSubmission.objects.filter(quiz=quiz)
    submitted_students = [sub.enrollment.student for sub in submitted]

    not_submitted = [en for en in enrollments if en.student not in submitted_students]

    return render(request, 'teacher/quiz_submissions_list.html', {
        'quiz': quiz,
        'submitted': submitted,
        'not_submitted': not_submitted
    })


def teacher_feedback_list(request):
    teacher_profile = get_object_or_404(TeacherProfile, user=request.user)

    # Get feedback only for courses handled by this teacher
    feedbacks = Feedback.objects.filter(course__teacher=teacher_profile).order_by("-created_at")

    return render(request, "teacher/teacher_feedback_list.html", {
        "feedbacks": feedbacks
    })
