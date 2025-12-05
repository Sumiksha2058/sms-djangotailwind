# core/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.http import JsonResponse, HttpResponseForbidden
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
)
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.db.models import Avg
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import (
    Course, Student, Subject, Teacher, Parent,
    UserProfile, Assignment, Attendance, Result, CustomRegisterForm
)

class RegisterView(CreateView):
    template_name = "auth/register.html"
    form_class = CustomRegisterForm
    success_url = reverse_lazy("login")

    def form_valid(self, form):
        user = form.save()
        UserProfile.objects.create(user=user)  # create linked profile
        return super().form_valid(form)


# import your existing project mixins (these should exist in core/mixins.py)
from .mixins import (
    AdminOnlyMixin,
    StaffAndAdminMixin,
    StudentAndAdminMixin,
    ParentAndAdminMixin,
    StudentOwnerMixin
)

from django.views.generic import FormView


class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('teacher', 'Teacher'),
        ('student', 'Student'),
        ('parent', 'Parent'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')

    def __str__(self):
        return f"{self.username} ({self.role})"


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # Optional extended info
    child = models.ForeignKey("Student", on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.username} Profile"
# -----------------------------
# Custom Login View
# -----------------------------
class CustomLoginView(FormView):
    template_name = 'core/templates/auth/login.html'
    form_class = AuthenticationForm
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        user = form.get_user()
        login(self.request, user)
        return super().form_valid(form)

# -----------------------------
# Register (Custom Form)
# -----------------------------
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()

    return render(request, 'auth/register.html', {'form': form})

@login_required
def home(request):
    user = request.user

    # --- ADMIN DASHBOARD ---
    if user.role == "admin":
        total_students = Student.objects.count()
        total_teachers = Teacher.objects.count()
        total_courses = Course.objects.count()
        total_subjects = Subject.objects.count()

        male = Student.objects.filter(gender='M').count()
        female = Student.objects.filter(gender='F').count()

        return render(request, "dashboard/admin_dashboard.html", {
            "total_students": total_students,
            "total_teachers": total_teachers,
            "total_courses": total_courses,
            "total_subjects": total_subjects,
            "male": male,
            "female": female,
        })

    # --- TEACHER DASHBOARD ---
    if user.role == "teacher":
        teacher = Teacher.objects.get(user=user)

        courses = Course.objects.filter(teacher=teacher)
        pending_assignments = Assignment.objects.filter(teacher=teacher, status="pending")
        attendance_links = courses  # teacher marks attendance for course

        return render(request, "dashboard/teacher_dashboard.html", {
            "courses": courses,
            "pending_assignments": pending_assignments,
            "attendance_links": attendance_links,
        })

    # --- STUDENT DASHBOARD ---
    if user.role == "student":
        student = Student.objects.get(user=user)

        upcoming_assignments = Assignment.objects.filter(course=student.course).order_by("due_date")[:5]
        recent_results = Result.objects.filter(student=student).order_by("-date")[:5]
        
        attendance_percentage = Attendance.objects.filter(student=student).aggregate(
            percent=models.Avg("percentage")
        )["percent"]

        return render(request, "dashboard/student_dashboard.html", {
            "upcoming_assignments": upcoming_assignments,
            "recent_results": recent_results,
            "attendance_percentage": attendance_percentage or 0,
        })

    # --- PARENT DASHBOARD ---
    if user.role == "parent":
        profile = UserProfile.objects.get(user=user)
        child = profile.child

        attendance = Attendance.objects.filter(student=child).aggregate(
            percent=models.Avg("percentage")
        )["percent"]

        results = Result.objects.filter(student=child)
        assignments = Assignment.objects.filter(course=child.course)

        return render(request, "dashboard/parent_dashboard.html", {
            "child": child,
            "attendance": attendance or 0,
            "results": results,
            "assignments": assignments,
        })

    # fallback
    return render(request, "home.html")

# -----------------------------
# Logout
# -----------------------------
def custom_logout(request):
    logout(request)
    return redirect('home')
# ---------------------------------------------------------------------
# Missing small mixins (we create these here as lightweight, safe versions)
# ---------------------------------------------------------------------

class StudentSelfUpdateMixin(UserPassesTestMixin):
    """
    Allow:
      - admins to edit any student
      - students to edit only their own Student record
    Adjust logic if your UserProfile structure differs.
    """
    def test_func(self):
        user = self.request.user
        if not user.is_authenticated:
            return False
        # allow admin (assuming role stored on user.userprofile.role)
        try:
            role = user.userprofile.role
        except Exception:
            role = None
        if role == "admin":
            return True

        # if student role, ensure the Student object being edited belongs to them
        if role == "student":
            # get pk from URL kwargs if present
            pk = self.kwargs.get("pk")
            if not pk:
                return False
            try:
                student = Student.objects.get(pk=pk)
            except Student.DoesNotExist:
                return False
            return getattr(student, "user_profile", None) == getattr(user, "userprofile", None)

        return False


class TeacherSelfAccessMixin(UserPassesTestMixin):
    """
    Allow:
      - admins to access any teacher
      - teachers to access only their own Teacher record
    """
    def test_func(self):
        user = self.request.user
        if not user.is_authenticated:
            return False

        try:
            role = user.userprofile.role
        except Exception:
            role = None

        if role == "admin":
            return True

        if role == "teacher":
            pk = self.kwargs.get("pk")
            if not pk:
                return False
            try:
                teacher = Teacher.objects.get(pk=pk)
            except Teacher.DoesNotExist:
                return False
            return getattr(teacher, "user_profile", None) == getattr(user, "userprofile", None)

        return False


# ---------------------------------------------------------------------
# Simple fallback predictor (replace with real ML logic later)
# ---------------------------------------------------------------------
def predict_pass_fail(attendance_percentage, avg_marks):
    """
    Return integer 1 for pass, 0 for fail (simple rule).
    Pass if avg_marks >= 40 and attendance >= 75.
    """
    try:
        attendance = float(attendance_percentage)
        avg = float(avg_marks)
    except Exception:
        return 0
    return 1 if avg >= 40 and attendance >= 75 else 0


# ---------------------------------------------------------------------
# Home view
# ---------------------------------------------------------------------
def home(request):
    return render(request, "home.html")


# ---------------------------------------------------------------------
# Analytics / Dashboard
# ---------------------------------------------------------------------
class AnalyticsListView(AdminOnlyMixin, TemplateView):
    template_name = "core/analytics.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        total_students = Student.objects.count()
        total_teachers = Teacher.objects.count()
        context["total_students"] = total_students
        context["total_teachers"] = total_teachers
        context["total_courses"] = Course.objects.count()
        context["total_subjects"] = Subject.objects.count()
        context["total_assignments"] = Assignment.objects.count()
        context["total_results"] = Result.objects.count()
        context["total_attendance_records"] = Attendance.objects.count()

        context["ts_ratio"] = round(total_students / total_teachers, 1) if total_teachers else 0

        # gender stats if field exists on Student
        male = Student.objects.filter(gender="male").count() if hasattr(Student, "gender") else 0
        female = Student.objects.filter(gender="female").count() if hasattr(Student, "gender") else 0
        other = Student.objects.filter(gender="other").count() if hasattr(Student, "gender") else 0
        context["gender_data"] = [male, female, other]

        # pass/fail stats (percentage field expected on Result)
        passed = Result.objects.filter(percentage__gte=40).count()
        failed = Result.objects.filter(percentage__lt=40).count()
        context["pass_fail_data"] = [passed, failed]

        # subject-wise average marks (use Avg correctly)
        labels = []
        values = []
        for sub in Subject.objects.all():
            avg = Result.objects.filter(subject=sub).aggregate(a=Avg("percentage"))["a"] or 0
            labels.append(sub.name)
            values.append(round(avg, 2))
        context["subject_labels"] = labels
        context["subject_values"] = values

        # placeholder
        context["avg_attendance"] = 87

        return context


# ---------------------------------------------------------------------
# Course CRUD
# ---------------------------------------------------------------------
class CourseListView(AdminOnlyMixin, ListView):
    model = Course
    template_name = "core/generic_list.html"
    context_object_name = "object_list"

    def get_context_data(self, **kwargs):
        c = super().get_context_data(**kwargs)
        c.update({
            "model_name": "course",
            "headers": ["Name", "Code", "Semester", "Capacity"],
            "fields": ["name", "code", "semester", "capacity"],
            "detail_url_name": "course_detail",
            "create_url_name": "course_create",
            "update_url_name": "course_update",
            "delete_url_name": "course_delete",
        })
        return c


class CourseDetailView(AdminOnlyMixin, DetailView):
    model = Course
    template_name = "core/course_detail.html"
    context_object_name = "course"


class CourseCreateView(AdminOnlyMixin, CreateView):
    model = Course
    template_name = "core/generic_form.html"
    fields = ["name", "code", "semester", "section", "capacity", "description", "class_teacher"]
    success_url = reverse_lazy("course_list")

    def get_context_data(self, **kwargs):
        c = super().get_context_data(**kwargs)
        c["model_name"] = "course"
        c["list_url_name"] = "course_list"
        return c


class CourseUpdateView(AdminOnlyMixin, UpdateView):
    model = Course
    template_name = "core/generic_form.html"
    fields = ["name", "code", "semester", "section", "capacity", "description", "class_teacher"]
    success_url = reverse_lazy("course_list")

    def get_context_data(self, **kwargs):
        c = super().get_context_data(**kwargs)
        c["model_name"] = "course"
        c["list_url_name"] = "course_list"
        return c


class CourseDeleteView(AdminOnlyMixin, DeleteView):
    model = Course
    template_name = "core/generic_confirm_delete.html"
    success_url = reverse_lazy("course_list")

    def get_context_data(self, **kwargs):
        c = super().get_context_data(**kwargs)
        c["model_name"] = "course"
        c["detail_url_name"] = "course_detail"
        return c


# ---------------------------------------------------------------------
# Student CRUD
# ---------------------------------------------------------------------
class StudentListView(StudentAndAdminMixin, ListView):
    model = Student
    template_name = "core/generic_list.html"
    context_object_name = "object_list"

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Student.objects.none()

        try:
            profile = user.userprofile
        except Exception:
            return Student.objects.none()

        if profile.role == "admin":
            return Student.objects.all()

        if profile.role == "teacher":
            teacher = Teacher.objects.filter(user_profile=profile).first()
            if teacher:
                # students in courses taught by this teacher
                return Student.objects.filter(course__class_teacher=teacher)

        if profile.role == "student":
            return Student.objects.filter(user_profile=profile)

        if profile.role == "parent":
            parent = Parent.objects.filter(user_profile=profile).first()
            if parent:
                return Student.objects.filter(parent=parent)

        return Student.objects.none()

    def get_context_data(self, **kwargs):
        c = super().get_context_data(**kwargs)
        c.update({
            "model_name": "student",
            "headers": ["Roll Number", "Student ID", "Course", "Status"],
            "fields": ["roll_number", "student_id", "course", "status"],
            "detail_url_name": "student_detail",
            "create_url_name": "student_create",
            "update_url_name": "student_update",
            "delete_url_name": "student_delete",
        })
        return c


class StudentDetailView(StudentOwnerMixin, DetailView):
    model = Student
    template_name = "core/student_detail.html"
    context_object_name = "student"


class StudentCreateView(AdminOnlyMixin, CreateView):
    # Only admins create students here — adjust if staff should create
    model = Student
    template_name = "core/generic_form.html"
    fields = [
        "user_profile", "student_id", "roll_number", "course", "date_of_birth",
        "address", "city", "state", "pin_code", "parent", "admission_date", "status"
    ]
    success_url = reverse_lazy("student_list")

    def get_context_data(self, **kwargs):
        c = super().get_context_data(**kwargs)
        c["model_name"] = "student"
        c["list_url_name"] = "student_list"
        return c


class StudentUpdateView(StudentSelfUpdateMixin, UpdateView):
    model = Student
    template_name = "core/generic_form.html"
    fields = [
        "user_profile", "student_id", "roll_number", "course", "date_of_birth",
        "address", "city", "state", "pin_code", "parent", "admission_date", "status"
    ]
    success_url = reverse_lazy("student_list")

    def get_context_data(self, **kwargs):
        c = super().get_context_data(**kwargs)
        c["model_name"] = "student"
        c["list_url_name"] = "student_list"
        return c


class StudentDeleteView(AdminOnlyMixin, DeleteView):
    model = Student
    template_name = "core/generic_confirm_delete.html"
    success_url = reverse_lazy("student_list")

    def get_context_data(self, **kwargs):
        c = super().get_context_data(**kwargs)
        c["model_name"] = "student"
        c["detail_url_name"] = "student_detail"
        return c


# ---------------------------------------------------------------------
# Subject CRUD
# ---------------------------------------------------------------------
class SubjectListView(AdminOnlyMixin, ListView):
    model = Subject
    template_name = "core/generic_list.html"
    context_object_name = "object_list"

    def get_context_data(self, **kwargs):
        c = super().get_context_data(**kwargs)
        c.update({
            "model_name": "subject",
            "headers": ["Name", "Code", "Credits", "Description"],
            "fields": ["name", "code", "credits", "description"],
            "detail_url_name": "subject_detail",
            "create_url_name": "subject_create",
            "update_url_name": "subject_update",
            "delete_url_name": "subject_delete",
        })
        return c


class SubjectDetailView(AdminOnlyMixin, DetailView):
    model = Subject
    template_name = "core/subject_detail.html"
    context_object_name = "subject"


class SubjectCreateView(AdminOnlyMixin, CreateView):
    model = Subject
    template_name = "core/generic_form.html"
    fields = ["name", "code", "credits", "description"]
    success_url = reverse_lazy("subject_list")


class SubjectUpdateView(AdminOnlyMixin, UpdateView):
    model = Subject
    template_name = "core/generic_form.html"
    fields = ["name", "code", "credits", "description"]
    success_url = reverse_lazy("subject_list")


class SubjectDeleteView(AdminOnlyMixin, DeleteView):
    model = Subject
    template_name = "core/generic_confirm_delete.html"
    success_url = reverse_lazy("subject_list")


# ---------------------------------------------------------------------
# Teacher CRUD
# ---------------------------------------------------------------------
class TeacherListView(StaffAndAdminMixin, ListView):
    model = Teacher
    template_name = "core/generic_list.html"
    context_object_name = "object_list"

    def get_context_data(self, **kwargs):
        c = super().get_context_data(**kwargs)
        c.update({
            "model_name": "teacher",
            "headers": ["Employee ID", "Qualification", "Department"],
            "fields": ["employee_id", "qualification", "department"],
            "detail_url_name": "teacher_detail",
            "create_url_name": "teacher_create",
            "update_url_name": "teacher_update",
            "delete_url_name": "teacher_delete",
        })
        return c


class TeacherDetailView(TeacherSelfAccessMixin, DetailView):
    model = Teacher
    template_name = "core/teacher_detail.html"
    context_object_name = "teacher"


class TeacherCreateView(StaffAndAdminMixin, CreateView):
    model = Teacher
    template_name = "core/generic_form.html"
    fields = ["user_profile", "employee_id", "qualification", "specialization", "joining_date", "department"]
    success_url = reverse_lazy("teacher_list")


class TeacherUpdateView(TeacherSelfAccessMixin, UpdateView):
    model = Teacher
    template_name = "core/generic_form.html"
    fields = ["user_profile", "employee_id", "qualification", "specialization", "joining_date", "department"]
    success_url = reverse_lazy("teacher_list")


class TeacherDeleteView(AdminOnlyMixin, DeleteView):
    model = Teacher
    template_name = "core/generic_confirm_delete.html"
    success_url = reverse_lazy("teacher_list")


# ---------------------------------------------------------------------
# Attendance CRUD
# ---------------------------------------------------------------------
class AttendanceListView(AdminOnlyMixin, ListView):
    model = Attendance
    template_name = "core/generic_list.html"
    context_object_name = "object_list"

    def get_context_data(self, **kwargs):
        c = super().get_context_data(**kwargs)
        c.update({
            "model_name": "attendance",
            "headers": ["Student", "Subject", "Date", "Status"],
            "fields": ["student", "subject", "attendance_date", "status"],
            "detail_url_name": "attendance_detail",
            "create_url_name": "attendance_create",
            "update_url_name": "attendance_update",
            "delete_url_name": "attendance_delete",
        })
        return c


class AttendanceDetailView(AdminOnlyMixin, DetailView):
    model = Attendance
    template_name = "core/attendance_detail.html"
    context_object_name = "attendance"


class AttendanceCreateView(AdminOnlyMixin, CreateView):
    model = Attendance
    template_name = "core/generic_form.html"
    fields = ["student", "subject", "attendance_date", "status", "remarks"]
    success_url = reverse_lazy("attendance_list")


class AttendanceUpdateView(AdminOnlyMixin, UpdateView):
    model = Attendance
    template_name = "core/generic_form.html"
    fields = ["student", "subject", "attendance_date", "status", "remarks"]
    success_url = reverse_lazy("attendance_list")


class AttendanceDeleteView(AdminOnlyMixin, DeleteView):
    model = Attendance
    template_name = "core/generic_confirm_delete.html"
    success_url = reverse_lazy("attendance_list")


# ---------------------------------------------------------------------
# Assignment CRUD
# ---------------------------------------------------------------------
class AssignmentListView(AdminOnlyMixin, ListView):
    model = Assignment
    template_name = "core/generic_list.html"
    context_object_name = "object_list"


class AssignmentDetailView(AdminOnlyMixin, DetailView):
    model = Assignment
    template_name = "core/assignment_detail.html"
    context_object_name = "assignment"


class AssignmentCreateView(AdminOnlyMixin, CreateView):
    model = Assignment
    template_name = "core/generic_form.html"
    fields = ["subject", "teacher", "title", "description", "due_date", "total_marks"]
    success_url = reverse_lazy("assignment_list")


class AssignmentUpdateView(AdminOnlyMixin, UpdateView):
    model = Assignment
    template_name = "core/generic_form.html"
    fields = ["subject", "teacher", "title", "description", "due_date", "total_marks"]
    success_url = reverse_lazy("assignment_list")


class AssignmentDeleteView(AdminOnlyMixin, DeleteView):
    model = Assignment
    template_name = "core/generic_confirm_delete.html"
    success_url = reverse_lazy("assignment_list")


# ---------------------------------------------------------------------
# Result CRUD
# ---------------------------------------------------------------------
class ResultListView(AdminOnlyMixin, ListView):
    model = Result
    template_name = "core/generic_list.html"
    context_object_name = "object_list"

    def get_context_data(self, **kwargs):
        c = super().get_context_data(**kwargs)
        c.update({
            "model_name": "result",
            "headers": ["Student", "Subject", "Exam", "Marks"],
            "fields": ["student", "subject", "exam", "marks_obtained"],
            "detail_url_name": "result_detail",
            "create_url_name": "result_create",
            "update_url_name": "result_update",
            "delete_url_name": "result_delete",
        })
        return c


class ResultDetailView(AdminOnlyMixin, DetailView):
    model = Result
    template_name = "core/result_detail.html"
    context_object_name = "result"


class ResultCreateView(AdminOnlyMixin, CreateView):
    model = Result
    template_name = "core/generic_form.html"
    fields = ["student", "subject", "exam", "marks_obtained", "total_marks", "percentage", "grade", "remarks"]
    success_url = reverse_lazy("result_list")


class ResultUpdateView(AdminOnlyMixin, UpdateView):
    model = Result
    template_name = "core/generic_form.html"
    fields = ["student", "subject", "exam", "marks_obtained", "total_marks", "percentage", "grade", "remarks"]
    success_url = reverse_lazy("result_list")


class ResultDeleteView(AdminOnlyMixin, DeleteView):
    model = Result
    template_name = "core/generic_confirm_delete.html"
    success_url = reverse_lazy("result_list")


# ---------------------------------------------------------------------
# Prediction API
# ---------------------------------------------------------------------
def student_prediction(request, pk):
    student = get_object_or_404(Student, pk=pk)

    total = student.attendance_set.count()
    present = student.attendance_set.filter(status="Present").count()
    attendance_percentage = (present / total * 100) if total > 0 else 0

    avg_marks = Result.objects.filter(student=student).aggregate(a=Avg("marks_obtained"))["a"] or 0

    prediction = predict_pass_fail(attendance_percentage, avg_marks)

    return JsonResponse({
        "student": getattr(student, "student_id", str(student.pk)),
        "attendance": attendance_percentage,
        "avg_marks": avg_marks,
        "prediction": "Pass" if prediction == 1 else "Fail"
    })
