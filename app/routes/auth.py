from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user

from app.forms.auth_forms import LoginForm
from app.services import AuthenticationError, ValidationError
from app.services.auth_service import AuthService

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


def _get_client_ip() -> str | None:
    forwarded_for = request.headers.get("X-Forwarded-For", "").split(",")[0].strip()
    return forwarded_for or request.remote_addr


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for("admin.dashboard"))
        return redirect(url_for("profile.dashboard"))

    form = LoginForm()

    if form.validate_on_submit():
        try:
            user = AuthService.login(
                identifier=form.identifier.data,
                password=form.password.data,
                remember=form.remember_me.data,
                ip_address=_get_client_ip(),
            )

            flash("Login successful.", "success")

            next_url = request.args.get("next")
            if next_url:
                return redirect(next_url)

            if user.is_admin:
                return redirect(url_for("admin.dashboard"))

            return redirect(url_for("profile.dashboard"))

        except AuthenticationError as exc:
            flash(str(exc), "danger")
        except ValidationError as exc:
            flash(str(exc), "warning")
        except Exception:
            flash("An unexpected error occurred during login.", "danger")

    return render_template("auth/login.html", form=form)


@auth_bp.route("/logout", methods=["POST"])
def logout():
    try:
        AuthService.logout(ip_address=_get_client_ip())
        flash("You have been logged out.", "info")
    except Exception:
        flash("Logout completed.", "info")

    return redirect(url_for("auth.login"))