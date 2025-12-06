from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.views import View
from django.contrib import messages
from django.db.models import Count, Avg
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from .forms import RegistrationForm
from .models import (
    Course,
    Student,
    Teacher,
    Subject,
    Parent,
    UserProfile,
    Assignment,
    Attendance,
    Result,
)

# ---------------------------------------------------
# AUTH VIEWS
# ---------------------------------------------------

class RegisterView(View):
    template_name = "auth/register.html"

    def get(self, request):
        return render(request, self.template_name, {"form": RegistrationForm()})

    def post(self, request):
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()

            # Auto-create UserProfile with default role "student"
            UserProfile.objects.create(user=user, role="student")

            messages.success(request, "Account created successfully!")
            return redirect("login")
        return render(request, self.template_name, {"form": form})


class CustomLoginView(View):
    template_name = "auth/login.html"

    def get(self, request):
        return render(request, self.template_name, {"form": AuthenticationForm()})

    def post(self, request):
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect("home")
        return render(request, self.template_name, {"form": form})


@login_required
def logout_view(request):
    logout(request)
    return redirect("login")


# ---------------------------------------------------
# ROLE-BASED DASHBOARD (Home)
# ---------------------------------------------------

@login_required
def home(request):
    # Prevent "DoesNotExist" error
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    # ---------------------- ADMIN DASHBOARD ----------------------
    if profile.role == "admin":
        context = {
            "role": "admin",
            "total_students": Student.objects.count(),
            "total_teachers": Teacher.objects.count(),
            "total_courses": Course.objects.count(),
            "total_subjects": Subject.objects.count(),
            "gender_stats": Student.objects.values("gender").annotate(count=Count("id")),
        }
        return render(request, "dashboard/admin_dashboard.html", context)

    # ---------------------- TEACHER DASHBOARD ----------------------
    if profile.role == "teacher":
        teacher = get_object_or_404(Teacher, user=request.user)

        return render(request, "dashboard/teacher_dashboard.html", {
            "role": "teacher",
            "teacher": teacher,
            "courses": Course.objects.filter(teacher=teacher),
            "pending_assignments": Assignment.objects.filter(
                teacher=teacher, status="pending"
            ),
        })

    # ---------------------- STUDENT DASHBOARD ----------------------
    if profile.role == "student":
        student = get_object_or_404(Student, user=request.user)

        return render(request, "dashboard/student_dashboard.html", {
            "role": "student",
            "student": student,
            "attendance_percent": Attendance.objects.filter(student=student)
                .aggregate(avg=Avg("status"))["avg"] or 0,
            "results": Result.objects.filter(student=student),
            "upcoming_assignments": Assignment.objects.filter(
                course__in=student.courses.all()
            ),
        })

    # ---------------------- PARENT DASHBOARD ----------------------
    if profile.role == "parent":
        parent = get_object_or_404(Parent, user=request.user)

        return render(request, "dashboard/parent_dashboard.html", {
            "role": "parent",
            "children": Student.objects.filter(parent=parent),
        })

    # Fallback (if no role assigned)
    return render(request, "home.html")


# ---------------------------------------------------
# GENERIC CRUD VIEWS
# ---------------------------------------------------

# COURSES
class CourseListView(ListView):
    model = Course
    template_name = "core/generic_list.html"


class CourseCreateView(CreateView):
    model = Course
    fields = "__all__"
    template_name = "core/form.html"
    success_url = reverse_lazy("course_list")


class CourseUpdateView(UpdateView):
    model = Course
    fields = "__all__"
    template_name = "core/form.html"
    success_url = reverse_lazy("course_list")


class CourseDeleteView(DeleteView):
    model = Course
    template_name = "core/delete_confirmation.html"
    success_url = reverse_lazy("course_list")


# STUDENTS
class StudentListView(ListView):
    model = Student
    template_name = "core/generic_list.html"


class StudentCreateView(CreateView):
    model = Student
    fields = "__all__"
    template_name = "core/form.html"
    success_url = reverse_lazy("student_list")


class StudentUpdateView(UpdateView):
    model = Student
    fields = "__all__"
    template_name = "core/form.html"
    success_url = reverse_lazy("student_list")


class StudentDeleteView(DeleteView):
    model = Student
    template_name = "core/delete_confirmation.html"
    success_url = reverse_lazy("student_list")


# TEACHERS
class TeacherListView(ListView):
    model = Teacher
    template_name = "core/generic_list.html"


class TeacherCreateView(CreateView):
    model = Teacher
    fields = "__all__"
    template_name = "core/form.html"
    success_url = reverse_lazy("teacher_list")


class TeacherUpdateView(UpdateView):
    model = Teacher
    fields = "__all__"
    template_name = "core/form.html"
    success_url = reverse_lazy("teacher_list")


# SUBJECTS
class SubjectListView(ListView):
    model = Subject
    template_name = "core/generic_list.html"


class SubjectCreateView(CreateView):
    model = Subject
    fields = "__all__"
    template_name = "core/form.html"
    success_url = reverse_lazy("subject_list")


# ASSIGNMENTS
class AssignmentListView(ListView):
    model = Assignment
    template_name = "core/generic_list.html"


class AssignmentCreateView(CreateView):
    model = Assignment
    fields = "__all__"
    template_name = "core/form.html"
    success_url = reverse_lazy("assignment_list")


# ATTENDANCE
class AttendanceListView(ListView):
    model = Attendance
    template_name = "core/generic_list.html"


# RESULTS
class ResultListView(ListView):
    model = Result
    template_name = "core/generic_list.html"
