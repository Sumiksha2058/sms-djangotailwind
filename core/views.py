from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.urls import reverse_lazy
from .models import Course, Student, Subject, Teacher, User, UserProfile, Assignment, Attendance, Result  

def home(request):
    return render(request, 'home.html')

# --- Dashboard Analylis  ---

class AnalyticsListView(TemplateView):
    template_name = "core/analytics.html"

class AnalyticsListView(TemplateView):
    template_name = "core/analytics.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # --- Basic Counts ---
        total_students = Student.objects.count()
        total_teachers = Teacher.objects.count()

        context["total_students"] = total_students
        context["total_teachers"] = total_teachers
        context["total_courses"] = Course.objects.count()
        context["total_subjects"] = Subject.objects.count()
        context["total_assignments"] = Assignment.objects.count()
        context["total_results"] = Result.objects.count()
        context["total_attendance_records"] = Attendance.objects.count()

        # Teacher : Student Ratio
        context["ts_ratio"] = round(total_students / total_teachers, 1) if total_teachers else 0

        # --- Gender Statistics (if Student model has gender field) ---
        male_count = Student.objects.filter(gender="male").count() if hasattr(Student, "gender") else 0
        female_count = Student.objects.filter(gender="female").count() if hasattr(Student, "gender") else 0
        other_count = Student.objects.filter(gender="other").count() if hasattr(Student, "gender") else 0

        context["gender_data"] = [male_count, female_count, other_count]

        # --- Result Statistics (Pass/Fail) ---
        pass_count = Result.objects.filter(percentage__gte=40).count()
        fail_count = Result.objects.filter(percentage__lt=40).count()

        context["pass_fail_data"] = [pass_count, fail_count]

        # --- Subject-Wise Average Marks ---
        subjects = Subject.objects.all()
        subject_labels = []
        subject_average = []

        for subject in subjects:
            results = Result.objects.filter(subject=subject)
            if results.exists():
                avg = results.aggregate(avg_marks=Subject.Avg("percentage"))["avg_marks"]
            else:
                avg = 0
            subject_labels.append(subject.name)
            subject_average.append(round(avg, 2))

        context["subject_labels"] = subject_labels
        context["subject_values"] = subject_average

        # --- Example Avg Attendance ---
        # (Replace with your real logic later)
        context["avg_attendance"] = 87  

        return context


# --- Course CRUD ---
class CourseListView(ListView):
    model = Course
    template_name = 'core/generic_list.html'
    context_object_name = 'object_list'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model_name'] = 'course'
        context['headers'] = ['Name', 'Code', 'Semester', 'Capacity']
        context['fields'] = ['name', 'code', 'semester', 'capacity']
        context['detail_url_name'] = 'course_detail'
        context['create_url_name'] = 'course_create'
        context['update_url_name'] = 'course_update'
        context['delete_url_name'] = 'course_delete'
        return context

class CourseDetailView(DetailView):
    model = Course
    template_name = 'core/course_detail.html'
    context_object_name = 'course'

class CourseCreateView(CreateView):
    model = Course
    template_name = 'core/generic_form.html'
    fields = ['name', 'code', 'semester', 'section', 'capacity', 'description', 'class_teacher']
    success_url = reverse_lazy('course_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model_name'] = 'course'
        context['list_url_name'] = 'course_list'
        return context

class CourseUpdateView(UpdateView):
    model = Course
    template_name = 'core/generic_form.html'
    fields = ['name', 'code', 'semester', 'section', 'capacity', 'description', 'class_teacher']
    success_url = reverse_lazy('course_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model_name'] = 'course'
        context['list_url_name'] = 'course_list'
        return context

class CourseDeleteView(DeleteView):
    model = Course
    template_name = 'core/generic_confirm_delete.html'
    success_url = reverse_lazy('course_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model_name'] = 'course'
        context['detail_url_name'] = 'course_detail'
        return context

# --- Student CRUD ---
class StudentListView(ListView):
    model = Student
    template_name = 'core/generic_list.html'
    context_object_name = 'object_list'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model_name'] = 'student'
        context['headers'] = ['Roll Number', 'Student ID', 'Course', 'Status']
        context['fields'] = ['roll_number', 'student_id', 'course', 'status']
        context['detail_url_name'] = 'student_detail'
        context['create_url_name'] = 'student_create'
        context['update_url_name'] = 'student_update'
        context['delete_url_name'] = 'student_delete'
        return context
    



class StudentDetailView(DetailView):
    model = Student
    template_name = 'core/student_detail.html'
    context_object_name = 'student'

class StudentCreateView(CreateView):
    model = Student
    template_name = 'core/generic_form.html'
    fields = ['student_id', 'roll_number', 'course', 'date_of_birth', 'address', 'city', 'state', 'pin_code', 'parent', 'admission_date', 'status']
    success_url = reverse_lazy('student_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model_name'] = 'student'
        context['list_url_name'] = 'student_list'
        return context

    def form_valid(self, form):
        # Create a new Django User and UserProfile for the student
        # This is a simplified approach, in a real app, this would be more complex
        username = f"student_{form.instance.roll_number}"
        user = User.objects.create_user(username=username, email=f"{username}@sms.com", password='password')
        UserProfile.objects.create(user=user, role='student')
        form.instance.user_profile = user.userprofile
        return super().form_valid(form)

class StudentUpdateView(UpdateView):
    model = Student
    template_name = 'core/generic_form.html'
    fields = ['student_id', 'roll_number', 'course', 'date_of_birth', 'address', 'city', 'state', 'pin_code', 'parent', 'admission_date', 'status']
    success_url = reverse_lazy('student_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model_name'] = 'student'
        context['list_url_name'] = 'student_list'
        return context

class StudentDeleteView(DeleteView):
    model = Student
    template_name = 'core/generic_confirm_delete.html'
    success_url = reverse_lazy('student_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model_name'] = 'student'
        context['detail_url_name'] = 'student_detail'
        return context

# --- Subject CRUD ---
class SubjectListView(ListView):
    model = Subject
    template_name = 'core/generic_list.html'
    context_object_name = 'object_list'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model_name'] = 'subject'
        context['headers'] = ['Name', 'Code', 'Credits']
        context['fields'] = ['name', 'code', 'credits']
        context['detail_url_name'] = 'subject_detail'
        context['create_url_name'] = 'subject_create'
        context['update_url_name'] = 'subject_update'
        context['delete_url_name'] = 'subject_delete'
        return context

class SubjectDetailView(DetailView):
    model = Subject
    template_name = 'core/subject_detail.html'
    context_object_name = 'subject'

class SubjectCreateView(CreateView):
    model = Subject
    template_name = 'core/generic_form.html'
    fields = ['name', 'code', 'credits', 'description']
    success_url = reverse_lazy('subject_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model_name'] = 'subject'
        context['list_url_name'] = 'subject_list'
        return context

class SubjectUpdateView(UpdateView):
    model = Subject
    template_name = 'core/generic_form.html'
    fields = ['name', 'code', 'credits', 'description']
    success_url = reverse_lazy('subject_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model_name'] = 'subject'
        context['list_url_name'] = 'subject_list'
        return context

class SubjectDeleteView(DeleteView):
    model = Subject
    template_name = 'core/generic_confirm_delete.html'
    success_url = reverse_lazy('subject_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model_name'] = 'subject'
        context['detail_url_name'] = 'subject_detail'
        return context

# --- Teacher CRUD ---
class TeacherListView(ListView):
    model = Teacher
    template_name = 'core/generic_list.html'
    context_object_name = 'object_list'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model_name'] = 'teacher'
        context['headers'] = ['Employee ID', 'Qualification', 'Department']
        context['fields'] = ['employee_id', 'qualification', 'department']
        context['detail_url_name'] = 'teacher_detail'
        context['create_url_name'] = 'teacher_create'
        context['update_url_name'] = 'teacher_update'
        context['delete_url_name'] = 'teacher_delete'
        return context

class TeacherDetailView(DetailView):
    model = Teacher
    template_name = 'core/teacher_detail.html'
    context_object_name = 'teacher'

class TeacherCreateView(CreateView):
    model = Teacher
    template_name = 'core/generic_form.html'
    fields = ['employee_id', 'qualification', 'specialization', 'joining_date', 'department']
    success_url = reverse_lazy('teacher_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model_name'] = 'teacher'
        context['list_url_name'] = 'teacher_list'
        return context

    def form_valid(self, form):
        # Create a new Django User and UserProfile for the teacher
        # This is a simplified approach, in a real app, this would be more complex
        username = f"teacher_{form.instance.employee_id}"
        user = User.objects.create_user(username=username, email=f"{username}@sms.com", password='password')
        UserProfile.objects.create(user=user, role='teacher')
        form.instance.user_profile = user.userprofile
        return super().form_valid(form)

class TeacherUpdateView(UpdateView):
    model = Teacher
    template_name = 'core/generic_form.html'
    fields = ['employee_id', 'qualification', 'specialization', 'joining_date', 'department']
    success_url = reverse_lazy('teacher_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model_name'] = 'teacher'
        context['list_url_name'] = 'teacher_list'
        return context

class TeacherDeleteView(DeleteView):
    model = Teacher
    template_name = 'core/generic_confirm_delete.html'
    success_url = reverse_lazy('teacher_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model_name'] = 'teacher'
        context['detail_url_name'] = 'teacher_detail'
        return context

# --- Attendance CRUD ---
class AttendanceListView(ListView):
    model = Attendance
    template_name = 'core/generic_list.html'
    context_object_name = 'object_list'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model_name'] = 'attendance'
        context['headers'] = ['Student', 'Subject', 'Date', 'Status']
        context['fields'] = ['student', 'subject', 'attendance_date', 'status']
        context['detail_url_name'] = 'attendance_detail'
        context['create_url_name'] = 'attendance_create'
        context['update_url_name'] = 'attendance_update'
        context['delete_url_name'] = 'attendance_delete'
        return context

class AttendanceDetailView(DetailView):
    model = Attendance
    template_name = 'core/attendance_detail.html'
    context_object_name = 'attendance'

class AttendanceCreateView(CreateView):
    model = Attendance
    template_name = 'core/generic_form.html'
    fields = ['student', 'subject', 'attendance_date', 'status', 'remarks']
    success_url = reverse_lazy('attendance_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model_name'] = 'attendance'
        context['list_url_name'] = 'attendance_list'
        return context

class AttendanceUpdateView(UpdateView):
    model = Attendance
    template_name = 'core/generic_form.html'
    fields = ['student', 'subject', 'attendance_date', 'status', 'remarks']
    success_url = reverse_lazy('attendance_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model_name'] = 'attendance'
        context['list_url_name'] = 'attendance_list'
        return context

class AttendanceDeleteView(DeleteView):
    model = Attendance
    template_name = 'core/generic_confirm_delete.html'
    success_url = reverse_lazy('attendance_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model_name'] = 'attendance'
        context['detail_url_name'] = 'attendance_detail'
        return context

# --- Assignment CRUD ---
class AssignmentListView(ListView):
    model = Assignment
    template_name = 'core/generic_list.html'
    context_object_name = 'object_list'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model_name'] = 'assignment'
        context['headers'] = ['Title', 'Subject', 'Teacher', 'Due Date']
        context['fields'] = ['title', 'subject', 'teacher', 'due_date']
        context['detail_url_name'] = 'assignment_detail'
        context['create_url_name'] = 'assignment_create'
        context['update_url_name'] = 'assignment_update'
        context['delete_url_name'] = 'assignment_delete'
        return context

class AssignmentDetailView(DetailView):
    model = Assignment
    template_name = 'core/assignment_detail.html'
    context_object_name = 'assignment'

class AssignmentCreateView(CreateView):
    model = Assignment
    template_name = 'core/generic_form.html'
    fields = ['subject', 'teacher', 'title', 'description', 'due_date', 'total_marks']
    success_url = reverse_lazy('assignment_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model_name'] = 'assignment'
        context['list_url_name'] = 'assignment_list'
        return context

class AssignmentUpdateView(UpdateView):
    model = Assignment
    template_name = 'core/generic_form.html'
    fields = ['subject', 'teacher', 'title', 'description', 'due_date', 'total_marks']
    success_url = reverse_lazy('assignment_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model_name'] = 'assignment'
        context['list_url_name'] = 'assignment_list'
        return context

class AssignmentDeleteView(DeleteView):
    model = Assignment
    template_name = 'core/generic_confirm_delete.html'
    success_url = reverse_lazy('assignment_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model_name'] = 'assignment'
        context['detail_url_name'] = 'assignment_detail'
        return context

# --- Result CRUD ---
class ResultListView(ListView):
    model = Result
    template_name = 'core/generic_list.html'
    context_object_name = 'object_list'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model_name'] = 'result'
        context['headers'] = ['Student', 'Subject', 'Exam', 'Marks']
        context['fields'] = ['student', 'subject', 'exam', 'marks_obtained']
        context['detail_url_name'] = 'result_detail'
        context['create_url_name'] = 'result_create'
        context['update_url_name'] = 'result_update'
        context['delete_url_name'] = 'result_delete'
        return context

class ResultDetailView(DetailView):
    model = Result
    template_name = 'core/result_detail.html'
    context_object_name = 'result'

class ResultCreateView(CreateView):
    model = Result
    template_name = 'core/generic_form.html'
    fields = ['student', 'subject', 'exam', 'marks_obtained', 'total_marks', 'percentage', 'grade', 'remarks']
    success_url = reverse_lazy('result_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model_name'] = 'result'
        context['list_url_name'] = 'result_list'
        return context

class ResultUpdateView(UpdateView):
    model = Result
    template_name = 'core/generic_form.html'
    fields = ['student', 'subject', 'exam', 'marks_obtained', 'total_marks', 'percentage', 'grade', 'remarks']
    success_url = reverse_lazy('result_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model_name'] = 'result'
        context['list_url_name'] = 'result_list'
        return context

class ResultDeleteView(DeleteView):
    model = Result
    template_name = 'core/generic_confirm_delete.html'
    success_url = reverse_lazy('result_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model_name'] = 'result'
        context['detail_url_name'] = 'result_detail'
        return context

def student_prediction(request, pk):
    student = Student.objects.get(pk=pk)

    attendance_total = student.attendance_set.count()
    attendance_present = student.attendance_set.filter(status="Present").count()
    attendance_percentage = (attendance_present / attendance_total * 100) if attendance_total > 0 else 0

    avg_marks = Result.objects.filter(student=student).aggregate(Avg("marks_obtained"))["marks_obtained__avg"] or 0

    prediction = predict_pass_fail(attendance_percentage, avg_marks)

    return JsonResponse({
        "student": student.student_id,
        "attendance": attendance_percentage,
        "avg_marks": avg_marks,
        "prediction": "Pass" if prediction == 1 else "Fail"
    })