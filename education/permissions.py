from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsTeacherOrReadOnly(BasePermission):
    """
    Students: read-only access
    Teachers/Admins: full CRUD access
    """

    def has_permission(self, request, view):
        # Allow read-only methods for everyone (GET, HEAD, OPTIONS)
        if request.method in SAFE_METHODS:
            return True

        # Block unauthenticated users
        if not request.user or not request.user.is_authenticated:
            return False

        # Allow teachers and superusers to modify data
        return request.user.role == "teacher" or request.user.is_superuser
