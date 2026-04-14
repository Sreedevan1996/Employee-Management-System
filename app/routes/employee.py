from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.forms.employee_forms import EmployeeForm
from app.services import ConflictError, NotFoundError, ValidationError
from app.services.auth_service import AuthService
from app.services.department_service import DepartmentService
from app.services.employee_service import EmployeeService
from app.utils.decorators import role_required

employee_bp = Blueprint("employee", __name__, url_prefix="/employees")


def _get_client_ip() -> str | None:
    forwarded_for = request.headers.get("X-Forwarded-For", "").split(",")[0].strip()
    return forwarded_for or request.remote_addr


def _safe_int(value, default=None):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _prepare_employee_form_choices(form):
    """
    Populate select-field choices dynamically.
    Expected fields in EmployeeForm:
      - department_id
      - user_id
    """
    departments = DepartmentService.list_departments(active_only=False)
    employee_users = AuthService.list_users(role="employee", active_only=True)

    if hasattr(form, "department_id"):
        form.department_id.choices = [(0, "Select Department")] + [
            (dept.id, f"{dept.name} ({dept.code})") for dept in departments
        ]

    if hasattr(form, "user_id"):
        form.user_id.choices = [(0, "No Linked User")] + [
            (user.id, f"{user.username} - {user.email}") for user in employee_users
        ]

    return departments, employee_users


@employee_bp.route("/")
@login_required
@role_required("admin")
def list_employees():
    search = request.args.get("search", "").strip() or None
    department_id = _safe_int(request.args.get("department_id"))
    active_only = request.args.get("active_only") == "1"

    employees = EmployeeService.list_employees(
        search=search,
        department_id=department_id,
        active_only=active_only,
    )
    departments = DepartmentService.list_departments(active_only=False)

    return render_template(
        "admin/employee_list.html",
        employees=employees,
        departments=departments,
        filters={
            "search": search,
            "department_id": department_id,
            "active_only": active_only,
        },
    )


@employee_bp.route("/create", methods=["GET", "POST"])
@login_required
@role_required("admin")
def create_employee():
    form = EmployeeForm()
    _prepare_employee_form_choices(form)

    if form.validate_on_submit():
        try:
            employee = EmployeeService.create_employee(
                data={
                    "employee_code": form.employee_code.data,
                    "first_name": form.first_name.data,
                    "last_name": form.last_name.data,
                    "email": form.email.data,
                    "phone": form.phone.data,
                    "job_title": form.job_title.data,
                    "address": form.address.data,
                    "salary": form.salary.data,
                    "date_joined": form.date_joined.data,
                    "department_id": form.department_id.data,
                    "user_id": form.user_id.data,
                    "is_active": form.is_active.data,
                },
                actor_id=current_user.id,
                ip_address=_get_client_ip(),
            )
            flash("Employee created successfully.", "success")
            return redirect(url_for("employee.view_employee", employee_id=employee.id))

        except ConflictError as exc:
            flash(str(exc), "danger")
        except ValidationError as exc:
            flash(str(exc), "warning")
        except Exception:
            flash("Failed to create employee.", "danger")

    return render_template(
        "admin/employee_form.html",
        form=form,
        page_title="Create Employee",
        submit_label="Create",
        employee=None,
    )


@employee_bp.route("/<int:employee_id>")
@login_required
@role_required("admin")
def view_employee(employee_id: int):
    try:
        employee = EmployeeService.get_employee_by_id(employee_id)
        return render_template("admin/employee_form.html", employee=employee, view_only=True)
    except NotFoundError as exc:
        flash(str(exc), "danger")
        return redirect(url_for("employee.list_employees"))


@employee_bp.route("/<int:employee_id>/edit", methods=["GET", "POST"])
@login_required
@role_required("admin")
def edit_employee(employee_id: int):
    try:
        employee = EmployeeService.get_employee_by_id(employee_id)
    except NotFoundError as exc:
        flash(str(exc), "danger")
        return redirect(url_for("employee.list_employees"))

    form = EmployeeForm(obj=employee)
    _prepare_employee_form_choices(form)

    if request.method == "GET":
        if hasattr(form, "department_id"):
            form.department_id.data = employee.department_id or 0
        if hasattr(form, "user_id"):
            form.user_id.data = employee.user_id or 0

    if form.validate_on_submit():
        try:
            EmployeeService.update_employee(
                employee_id=employee.id,
                data={
                    "employee_code": form.employee_code.data,
                    "first_name": form.first_name.data,
                    "last_name": form.last_name.data,
                    "email": form.email.data,
                    "phone": form.phone.data,
                    "job_title": form.job_title.data,
                    "address": form.address.data,
                    "salary": form.salary.data,
                    "date_joined": form.date_joined.data,
                    "department_id": form.department_id.data,
                    "user_id": form.user_id.data,
                    "is_active": form.is_active.data,
                },
                actor_id=current_user.id,
                ip_address=_get_client_ip(),
            )
            flash("Employee updated successfully.", "success")
            return redirect(url_for("employee.view_employee", employee_id=employee.id))

        except ConflictError as exc:
            flash(str(exc), "danger")
        except ValidationError as exc:
            flash(str(exc), "warning")
        except Exception:
            flash("Failed to update employee.", "danger")

    return render_template(
        "admin/employee_form.html",
        form=form,
        page_title="Edit Employee",
        submit_label="Update",
        employee=employee,
    )


@employee_bp.route("/<int:employee_id>/delete", methods=["POST"])
@login_required
@role_required("admin")
def delete_employee(employee_id: int):
    try:
        EmployeeService.delete_employee(
            employee_id=employee_id,
            actor_id=current_user.id,
            ip_address=_get_client_ip(),
        )
        flash("Employee deleted successfully.", "success")

    except NotFoundError as exc:
        flash(str(exc), "danger")
    except Exception:
        flash("Failed to delete employee.", "danger")

    return redirect(url_for("employee.list_employees"))