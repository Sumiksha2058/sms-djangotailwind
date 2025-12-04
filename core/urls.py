from django.urls import path, include
from . import views
# from core.views import home
from .views import (
    CourseListView, CourseDetailView, CourseCreateView, CourseUpdateView, CourseDeleteView,
    StudentListView, StudentDetailView, StudentCreateView, StudentUpdateView, StudentDeleteView,
    SubjectListView, SubjectDetailView, SubjectCreateView, SubjectUpdateView, SubjectDeleteView,
    TeacherListView, TeacherDetailView, TeacherCreateView, TeacherUpdateView, TeacherDeleteView,
    AttendanceListView, AttendanceDetailView, AttendanceCreateView, AttendanceUpdateView, AttendanceDeleteView,
    AssignmentListView, AssignmentDetailView, AssignmentCreateView, AssignmentUpdateView, AssignmentDeleteView,
    ResultListView, ResultDetailView, ResultCreateView, ResultUpdateView, ResultDeleteView, home, AnalyticsListView
)

urlpatterns = [
    path('', views.home, name='home'),

    # Course URLs
    path('courses/', CourseListView.as_view(), name='course_list'),
    path('courses/<int:pk>/', CourseDetailView.as_view(), name='course_detail'),
    path('courses/new/', CourseCreateView.as_view(), name='course_create'),
    path('courses/<int:pk>/edit/', CourseUpdateView.as_view(), name='course_update'),
    path('courses/<int:pk>/delete/', CourseDeleteView.as_view(), name='course_delete'),

    # Student URLs
    path('students/', StudentListView.as_view(), name='student_list'),
    path('students/<int:pk>/', StudentDetailView.as_view(), name='student_detail'),
    path('students/new/', StudentCreateView.as_view(), name='student_create'),
    path('students/<int:pk>/edit/', StudentUpdateView.as_view(), name='student_update'),
    path('students/<int:pk>/delete/', StudentDeleteView.as_view(), name='student_delete'),

    # Subject URLs
    path('subjects/', SubjectListView.as_view(), name='subject_list'),
    path('subjects/<int:pk>/', SubjectDetailView.as_view(), name='subject_detail'),
    path('subjects/new/', SubjectCreateView.as_view(), name='subject_create'),
    path('subjects/<int:pk>/edit/', SubjectUpdateView.as_view(), name='subject_update'),
    path('subjects/<int:pk>/delete/', SubjectDeleteView.as_view(), name='subject_delete'),

    # Teacher URLs
    path('teachers/', TeacherListView.as_view(), name='teacher_list'),
    path('teachers/<int:pk>/', TeacherDetailView.as_view(), name='teacher_detail'),
    path('teachers/new/', TeacherCreateView.as_view(), name='teacher_create'),
    path('teachers/<int:pk>/edit/', TeacherUpdateView.as_view(), name='teacher_update'),
    path('teachers/<int:pk>/delete/', TeacherDeleteView.as_view(), name='teacher_delete'),

    # Attendance URLs
    path('attendance/', AttendanceListView.as_view(), name='attendance_list'),
    path('attendance/<int:pk>/', AttendanceDetailView.as_view(), name='attendance_detail'),
    path('attendance/new/', AttendanceCreateView.as_view(), name='attendance_create'),
    path('attendance/<int:pk>/edit/', AttendanceUpdateView.as_view(), name='attendance_update'),
    path('attendance/<int:pk>/delete/', AttendanceDeleteView.as_view(), name='attendance_delete'),

    # Assignment URLs
    path('assignments/', AssignmentListView.as_view(), name='assignment_list'),
    path('assignments/<int:pk>/', AssignmentDetailView.as_view(), name='assignment_detail'),
    path('assignments/new/', AssignmentCreateView.as_view(), name='assignment_create'),
    path('assignments/<int:pk>/edit/', AssignmentUpdateView.as_view(), name='assignment_update'),
    path('assignments/<int:pk>/delete/', AssignmentDeleteView.as_view(), name='assignment_delete'),

    # Result URLs
    path('results/', ResultListView.as_view(), name='result_list'),
    path('results/<int:pk>/', ResultDetailView.as_view(), name='result_detail'),
    path('results/new/', ResultCreateView.as_view(), name='result_create'),
    path('results/<int:pk>/edit/', ResultUpdateView.as_view(), name='result_update'),
    path('results/<int:pk>/delete/', ResultDeleteView.as_view(), name='result_delete'),

    # Analytics URLs
    path("analytics/", AnalyticsListView.as_view(), name="analytics"),
]
