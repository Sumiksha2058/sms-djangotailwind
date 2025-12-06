from django.urls import path
from .views import (
    RegisterView, CustomLoginView, logout_view,
    CourseListView, CourseCreateView, CourseUpdateView, CourseDeleteView,
    StudentListView, StudentCreateView, StudentUpdateView, StudentDeleteView,
    TeacherListView, TeacherCreateView, TeacherUpdateView,
    SubjectListView, SubjectCreateView,
    AssignmentListView, AssignmentCreateView,
    AttendanceListView, ResultListView,
    home
)

urlpatterns = [
    path("", home, name="home"),

    # Auth
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", CustomLoginView.as_view(), name="login"),
    path("logout/", logout_view, name="logout"),

    # Course CRUD
    path("courses/", CourseListView.as_view(), name="course_list"),
    path("courses/add/", CourseCreateView.as_view(), name="course_add"),
    path("courses/<int:pk>/edit/", CourseUpdateView.as_view(), name="course_edit"),
    path("courses/<int:pk>/delete/", CourseDeleteView.as_view(), name="course_delete"),

    # Student CRUD
    path("students/", StudentListView.as_view(), name="student_list"),
    path("students/add/", StudentCreateView.as_view(), name="student_add"),
    path("students/<int:pk>/edit/", StudentUpdateView.as_view(), name="student_edit"),
    path("students/<int:pk>/delete/", StudentDeleteView.as_view(), name="student_delete"),

    # Teacher CRUD
    path("teachers/", TeacherListView.as_view(), name="teacher_list"),
    path("teachers/add/", TeacherCreateView.as_view(), name="teacher_add"),
    path("teachers/<int:pk>/edit/", TeacherUpdateView.as_view(), name="teacher_edit"),

    # Subject CRUD
    path("subjects/", SubjectListView.as_view(), name="subject_list"),
    path("subjects/add/", SubjectCreateView.as_view(), name="subject_add"),

    # Assignment CRUD
    path("assignments/", AssignmentListView.as_view(), name="assignment_list"),
    path("assignments/add/", AssignmentCreateView.as_view(), name="assignment_add"),

    # Attendance and Results
    path("attendance/", AttendanceListView.as_view(), name="attendance_list"),
    path("results/", ResultListView.as_view(), name="result_list"),
]
