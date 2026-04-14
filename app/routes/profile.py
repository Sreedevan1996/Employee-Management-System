from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.forms.employee_forms import ProfileForm
from app.services import NotFoundError, ValidationError
from app.services.employee_service import EmployeeService
from app.utils.decorators import role_required

profile_bp = Blueprint("profile", __name__, url_prefix="/profile")


def _get_client_ip() -> str | None:
    forwarded_for = request.headers.get("X-Forwarded-For", "").split(",")[0].strip()
    return forwarded_for or request.remote_addr


@profile_bp.route("/dashboard")
@login_required
@role_required("employee")
def dashboard():
    try:
        employee = EmployeeService.get_employee_by_user_id(current_user.id)
        return render_template("employee/dashboard.html", employee=employee)
    except NotFoundError as exc:
        flash(str(exc), "warning")
        return redirect(url_for("main.index"))


@profile_bp.route("/")
@login_required
@role_required("employee")
def view_profile():
    try:
        employee = EmployeeService.get_employee_by_user_id(current_user.id)
        return render_template("employee/profile.html", employee=employee)
    except NotFoundError as exc:
        flash(str(exc), "warning")
        return redirect(url_for("main.index"))


@profile_bp.route("/edit", methods=["GET", "POST"])
@login_required
@role_required("employee")
def edit_profile():
    try:
        employee = EmployeeService.get_employee_by_user_id(current_user.id)
    except NotFoundError as exc:
        flash(str(exc), "warning")
        return redirect(url_for("main.index"))

    form = ProfileForm(obj=employee)

    if form.validate_on_submit():
        try:
            EmployeeService.update_own_profile(
                user_id=current_user.id,
                data={
                    "phone": form.phone.data,
                    "address": form.address.data,
                },
                ip_address=_get_client_ip(),
            )
            flash("Profile updated successfully.", "success")
            return redirect(url_for("profile.view_profile"))

        except ValidationError as exc:
            flash(str(exc), "warning")
        except Exception:
            flash("Failed to update profile.", "danger")

    return render_template(
        "employee/profile_edit.html",
        form=form,
        employee=employee,
    )