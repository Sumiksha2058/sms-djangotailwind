from django.contrib.auth.mixins import UserPassesTestMixin

class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser

class TeacherRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return hasattr(self.request.user, "teacher")

class StudentRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return hasattr(self.request.user, "student")

class ParentRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return hasattr(self.request.user, "parent")
