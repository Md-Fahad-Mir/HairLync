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
    """Allow access only to barber/hair stylist users."""
    message = "Only barbers/hair stylists can access this resource."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == 'barber'
        )


class IsSalon(BasePermission):
    """Allow access only to salon users (both owner and employee)."""
    message = "Only salons can access this resource."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == 'salon'
        )


class IsSalonOwner(BasePermission):
    """Allow access only to salon OWNER accounts (not sub-profiles)."""
    message = "Only salon owners can access this resource."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == 'salon'
            and not request.user.is_sub_profile
        )


class IsSalonEmployee(BasePermission):
    """Allow access only to salon EMPLOYEE sub-profile accounts."""
    message = "Only salon employees can access this resource."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == 'salon'
            and request.user.is_sub_profile
        )


class IsSalonOrEmployee(BasePermission):
    """Allow access to salon owners OR their employees."""
    message = "Only salon owners or their employees can access this resource."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.role == 'salon'


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


class IsNotSubProfile(BasePermission):
    """
    Deny access to sub-profile (employee) users for restricted actions.
    Sub-profiles cannot: delete accounts, create sub-profiles, manage the salon.
    """
    message = "Sub-profile accounts cannot perform this action."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return not request.user.is_sub_profile
