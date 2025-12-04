from django.contrib import admin
from .models import (
    UserProfile, Course, Subject, Teacher, Parent, Student,
    CourseSubject, TeacherSubject, Attendance, Assignment,
    AssignmentSubmission, Exam, Result, Timetable
)

# Register your models here.
admin.site.register(UserProfile)
admin.site.register(Course)
admin.site.register(Subject)
admin.site.register(Teacher)
admin.site.register(Parent)
admin.site.register(Student)
admin.site.register(CourseSubject)
admin.site.register(TeacherSubject)
admin.site.register(Attendance)
admin.site.register(Assignment)
admin.site.register(AssignmentSubmission)
admin.site.register(Exam)
admin.site.register(Result)
admin.site.register(Timetable)
