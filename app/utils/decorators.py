from functools import wraps

from flask import abort, flash, redirect, request, url_for
from flask_login import current_user


def role_required(*allowed_roles):
    """
    Ensure the current user is authenticated and has one of the allowed roles.

    Usage:
        @role_required("admin")
        @role_required("employee")
        @role_required("admin", "employee")
    """
    normalized_roles = {role.strip().lower() for role in allowed_roles if role}

    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(*args, **kwargs):
            if not current_user.is_authenticated:
                flash("Please log in to continue.", "warning")
                return redirect(url_for("auth.login", next=request.url))

            user_role = getattr(current_user, "role", None)
            if user_role not in normalized_roles:
                abort(403)

            if not getattr(current_user, "is_active", False):
                flash("Your account is inactive. Please contact an administrator.", "danger")
                return redirect(url_for("auth.logout"))

            return view_func(*args, **kwargs)

        return wrapped_view

    return decorator


def admin_required(view_func):
    """
    Convenience decorator for admin-only routes.
    """
    return role_required("admin")(view_func)


def employee_required(view_func):
    """
    Convenience decorator for employee-only routes.
    """
    return role_required("employee")(view_func)