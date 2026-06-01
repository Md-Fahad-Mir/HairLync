from rest_framework.permissions import BasePermission


class IsClient(BasePermission):
    """Allow access only to client users."""
    message = "Only clients can access this resource."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == 'client'
        )


class IsBarber(BasePermission):
    """Allow access only to barber/hairdresser users."""
    message = "Only barbers/hairdressers can access this resource."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == 'barber'
        )


class IsBarberOrSubBarber(BasePermission):
    """Allow access to barber owners and their employees."""
    message = "Only barbers or their employees can access this resource."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.role == 'barber':
            return True
        # Check if user is an employee (sub-barber)
        return hasattr(request.user, 'employee_profile')


class IsAdminUser(BasePermission):
    """Allow access only to admin users."""
    message = "Only administrators can access this resource."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and (request.user.role == 'admin' or request.user.is_staff)
        )


class IsOwnerOrAdmin(BasePermission):
    """Allow access to the object owner or admin users."""
    message = "You can only access your own resources."

    def has_object_permission(self, request, view, obj):
        if request.user.role == 'admin' or request.user.is_staff:
            return True
        if hasattr(obj, 'user'):
            return obj.user == request.user
        return obj == request.user


class IsSubscribedBarber(BasePermission):
    """Allow access only to barbers with an active subscription."""
    message = "An active subscription is required to access this feature."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == 'barber'
            and request.user.is_subscribed()
        )


class IsVerifiedUser(BasePermission):
    """Allow access only to verified users."""
    message = "Email verification is required."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.is_verified
        )
