# Course/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Course
from .forms import CourseForm

# ---------------------------
# ✅ Helper Functions
# ---------------------------
def is_admin(user):
    return user.is_authenticated and user.role == 'admin'

def is_teacher(user):
    return user.is_authenticated and user.role == 'teacher'

# ---------------------------
# 🧑‍💼 Admin Views
# ---------------------------
@login_required
@user_passes_test(is_admin)
def admin_course_list(request):
    courses = Course.objects.all()
    return render(request, 'course/admin_course_list.html', {'courses': courses})

@login_required
@user_passes_test(is_admin)
def create_course(request):
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('course:admin_course_list')
    else:
        form = CourseForm()
    return render(request, 'course/course_form.html', {'form': form, 'title': 'Add Course'})

@login_required
@user_passes_test(is_admin)
def edit_course(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            return redirect('course:admin_course_list')
    else:
        form = CourseForm(instance=course)
    return render(request, 'course/course_form.html', {'form': form, 'title': 'Edit Course'})

@login_required
@user_passes_test(is_admin)
def delete_course(request, pk):
    course = get_object_or_404(Course, pk=pk)
    course.delete()
    return redirect('course:admin_course_list')

# ---------------------------
# 👨‍🏫 Teacher Dashboard View
# ---------------------------
@login_required
def teacher_dashboard(request):
    teacher_profile = request.user.teacher_profile  # current logged-in teacher
    assigned_courses = Course.objects.filter(teacher=teacher_profile)

    context = {
        'teacher': teacher_profile,
        'courses': assigned_courses,
    }
    return render(request, 'teacher/teacher_dashboard.html', context)
