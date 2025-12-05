from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import get_object_or_404
from .models import UserProfile, Student, Teacher, Parent

class RoleRequiredMixin(UserPassesTestMixin):
    """Base mixin to check if the user has a specific role."""
    required_roles = []

    def test_func(self):
        if not self.request.user.is_authenticated:
            return False
        
        try:
            profile = self.request.user.userprofile
            # Admin can do everything
            if profile.role == 'admin':
                return True
            
            # Check if the user's role is in the required roles list
            return profile.role in self.required_roles
        except UserProfile.DoesNotExist:
            return False

class AdminOnlyMixin(RoleRequiredMixin):
    """Only allows access to users with the 'admin' role."""
    required_roles = ['admin']

class StaffAndAdminMixin(RoleRequiredMixin):
    """Allows access to users with 'admin' or 'teacher' roles."""
    required_roles = ['teacher']

class StudentAndAdminMixin(RoleRequiredMixin):
    """Allows access to users with 'admin' or 'student' roles."""
    required_roles = ['student']

class ParentAndAdminMixin(RoleRequiredMixin):
    """Allows access to users with 'admin' or 'parent' roles."""
    required_roles = ['parent']

class StudentOwnerMixin(UserPassesTestMixin):
    """Allows access to the student, their parent, or an admin/teacher."""
    def test_func(self):
        if not self.request.user.is_authenticated:
            return False
        
        try:
            profile = self.request.user.userprofile
            if profile.role == 'admin' or profile.role == 'teacher':
                return True
            
            student = get_object_or_404(Student, pk=self.kwargs['pk'])
            
            # Student can view their own detail
            if profile.role == 'student' and student.user_profile == profile:
                return True
            
            # Parent can view their child's detail
            if profile.role == 'parent':
                try:
                    parent = Parent.objects.get(user_profile=profile)
                    if student.parent == parent:
                        return True
                except Parent.DoesNotExist:
                    pass
                    
            return False
        except UserProfile.DoesNotExist:
            return False
        except Student.DoesNotExist:
            # If student doesn't exist, let the view handle the 404, but deny access based on role check
            return False

class TeacherSelfAccessMixin(UserPassesTestMixin):
    """Allows access to the teacher themselves or an admin."""
    def test_func(self):
        if not self.request.user.is_authenticated:
            return False
        
        try:
            profile = self.request.user.userprofile
            if profile.role == 'admin':
                return True
            
            teacher = get_object_or_404(Teacher, pk=self.kwargs['pk'])
            
            # Teacher can view/update their own detail
            if profile.role == 'teacher' and teacher.user_profile == profile:
                return True
                    
            return False
        except UserProfile.DoesNotExist:
            return False
        except Teacher.DoesNotExist:
            return False

class StudentSelfUpdateMixin(UserPassesTestMixin):
    """Allows access to the student themselves or an admin for update."""
    def test_func(self):
        if not self.request.user.is_authenticated:
            return False
        
        try:
            profile = self.request.user.userprofile
            if profile.role == 'admin':
                return True
            
            student = get_object_or_404(Student, pk=self.kwargs['pk'])
            
            # Student can update their own detail
            if profile.role == 'student' and student.user_profile == profile:
                return True
                    
            return False
        except UserProfile.DoesNotExist:
            return False
        except Student.DoesNotExist:
            return False
