from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.forms.department_forms import DepartmentForm
from app.models.department import Department
from app.models.employee import Employee
from app.models.user import User
from app.services import ConflictError, NotFoundError, ValidationError, AuthorizationError
from app.services.audit_service import AuditService
from app.services.auth_service import AuthService
from app.services.department_service import DepartmentService
from app.utils.decorators import role_required

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def _get_client_ip() -> str | None:
    forwarded_for = request.headers.get("X-Forwarded-For", "").split(",")[0].strip()
    return forwarded_for or request.remote_addr


def _safe_int(value, default=None):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


@admin_bp.route("/dashboard")
@login_required
@role_required("admin")
def dashboard():
    stats = {
        "user_count": User.query.count(),
        "employee_count": Employee.query.count(),
        "department_count": Department.query.count(),
        "recent_logs": AuditService.list_logs(limit=10),
    }
    return render_template("admin/dashboard.html", stats=stats)


@admin_bp.route("/users", methods=["GET", "POST"])
@login_required
@role_required("admin")
def users():
    """
    Combined user list + create user route.
    Uses request.form directly so no separate user_forms.py is required.
    """
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        role = request.form.get("role", "employee").strip().lower()

        try:
            AuthService.create_user(
                username=username,
                email=email,
                password=password,
                role=role,
                actor_id=current_user.id,
                ip_address=_get_client_ip(),
            )
            flash("User account created successfully.", "success")
            return redirect(url_for("admin.users"))

        except ConflictError as exc:
            flash(str(exc), "danger")
        except ValidationError as exc:
            flash(str(exc), "warning")
        except Exception:
            flash("Failed to create user account.", "danger")

    role_filter = request.args.get("role", "").strip().lower() or None
    active_only = request.args.get("active_only") == "1"

    users_list = AuthService.list_users(role=role_filter, active_only=active_only)

    return render_template(
        "admin/users.html",
        users=users_list,
        selected_role=role_filter,
        active_only=active_only,
    )


@admin_bp.route("/users/<int:user_id>/toggle-active", methods=["POST"])
@login_required
@role_required("admin")
def toggle_user_active(user_id: int):
    try:
        user = AuthService.get_user_by_id(user_id)
        AuthService.set_user_active_status(
            user_id=user.id,
            is_active=not user.is_active,
            actor_id=current_user.id,
            ip_address=_get_client_ip(),
        )
        flash("User status updated successfully.", "success")

    except NotFoundError as exc:
        flash(str(exc), "danger")
    except ValidationError as exc:
        flash(str(exc), "warning")
    except Exception:
        flash("Failed to update user status.", "danger")

    return redirect(url_for("admin.users"))


@admin_bp.route("/users/<int:user_id>/reset-password", methods=["POST"])
@login_required
@role_required("admin")
def reset_user_password(user_id: int):
    new_password = request.form.get("new_password", "")

    try:
        AuthService.admin_reset_password(
            target_user_id=user_id,
            new_password=new_password,
            actor_id=current_user.id,
            ip_address=_get_client_ip(),
        )
        flash("Password reset successfully.", "success")

    except AuthorizationError as exc:
        flash(str(exc), "danger")
    except NotFoundError as exc:
        flash(str(exc), "danger")
    except ValidationError as exc:
        flash(str(exc), "warning")
    except Exception:
        flash("Failed to reset password.", "danger")

    return redirect(url_for("admin.users"))


@admin_bp.route("/departments")
@login_required
@role_required("admin")
def department_list():
    departments = DepartmentService.list_departments(active_only=False)
    return render_template("admin/department_list.html", departments=departments)


@admin_bp.route("/departments/create", methods=["GET", "POST"])
@login_required
@role_required("admin")
def create_department():
    form = DepartmentForm()

    if form.validate_on_submit():
        try:
            DepartmentService.create_department(
                name=form.name.data,
                code=form.code.data,
                description=form.description.data,
                manager_name=form.manager_name.data,
                actor_id=current_user.id,
                ip_address=_get_client_ip(),
            )
            flash("Department created successfully.", "success")
            return redirect(url_for("admin.department_list"))

        except ConflictError as exc:
            flash(str(exc), "danger")
        except ValidationError as exc:
            flash(str(exc), "warning")
        except Exception:
            flash("Failed to create department.", "danger")

    return render_template(
        "admin/department_form.html",
        form=form,
        page_title="Create Department",
        submit_label="Create",
        department=None,
    )


@admin_bp.route("/departments/<int:department_id>/edit", methods=["GET", "POST"])
@login_required
@role_required("admin")
def edit_department(department_id: int):
    try:
        department = DepartmentService.get_department_by_id(department_id)
    except NotFoundError as exc:
        flash(str(exc), "danger")
        return redirect(url_for("admin.department_list"))

    form = DepartmentForm(obj=department)

    if form.validate_on_submit():
        try:
            DepartmentService.update_department(
                department_id=department.id,
                name=form.name.data,
                code=form.code.data,
                description=form.description.data,
                manager_name=form.manager_name.data,
                is_active=form.is_active.data,
                actor_id=current_user.id,
                ip_address=_get_client_ip(),
            )
            flash("Department updated successfully.", "success")
            return redirect(url_for("admin.department_list"))

        except ConflictError as exc:
            flash(str(exc), "danger")
        except ValidationError as exc:
            flash(str(exc), "warning")
        except Exception:
            flash("Failed to update department.", "danger")

    return render_template(
        "admin/department_form.html",
        form=form,
        page_title="Edit Department",
        submit_label="Update",
        department=department,
    )


@admin_bp.route("/departments/<int:department_id>/delete", methods=["POST"])
@login_required
@role_required("admin")
def delete_department(department_id: int):
    try:
        DepartmentService.delete_department(
            department_id=department_id,
            actor_id=current_user.id,
            ip_address=_get_client_ip(),
        )
        flash("Department deleted successfully.", "success")

    except ConflictError as exc:
        flash(str(exc), "warning")
    except NotFoundError as exc:
        flash(str(exc), "danger")
    except Exception:
        flash("Failed to delete department.", "danger")

    return redirect(url_for("admin.department_list"))


@admin_bp.route("/audit-logs")
@login_required
@role_required("admin")
def audit_logs():
    user_id = _safe_int(request.args.get("user_id"))
    action = request.args.get("action", "").strip() or None
    status = request.args.get("status", "").strip() or None

    logs = AuditService.list_logs(
        user_id=user_id,
        action=action,
        status=status,
        limit=200,
    )

    return render_template(
        "admin/audit_logs.html",
        logs=logs,
        filters={
            "user_id": user_id,
            "action": action,
            "status": status,
        },
    )