import re

from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, SelectField, StringField, SubmitField
from wtforms.fields import EmailField
from wtforms.validators import (
    DataRequired,
    Email,
    EqualTo,
    Length,
    ValidationError,
    Optional,
)


def _strip_filter(value):
    return value.strip() if isinstance(value, str) else value


class UserCreateForm(FlaskForm):
    username = StringField(
        "Username",
        filters=[_strip_filter],
        validators=[
            DataRequired(message="Username is required."),
            Length(min=3, max=50, message="Username must be between 3 and 50 characters."),
        ],
        render_kw={"placeholder": "e.g. john.doe"},
    )

    email = EmailField(
        "Email",
        filters=[_strip_filter],
        validators=[
            DataRequired(message="Email is required."),
            Email(message="Enter a valid email address."),
            Length(max=120, message="Email cannot exceed 120 characters."),
        ],
        render_kw={"placeholder": "e.g. john@example.com"},
    )

    password = PasswordField(
        "Password",
        validators=[
            DataRequired(message="Password is required."),
            Length(min=8, max=128, message="Password must be at least 8 characters."),
        ],
        render_kw={"autocomplete": "new-password"},
    )

    confirm_password = PasswordField(
        "Confirm Password",
        validators=[
            DataRequired(message="Please confirm the password."),
            EqualTo("password", message="Passwords must match."),
        ],
        render_kw={"autocomplete": "new-password"},
    )

    role = SelectField(
        "Role",
        choices=[
            ("employee", "Employee"),
            ("admin", "Admin"),
        ],
        validators=[DataRequired(message="Role is required.")],
        default="employee",
    )

    is_active = BooleanField("Active", default=True)

    submit = SubmitField("Create User")

    def validate_username(self, field):
        value = (field.data or "").strip()
        if not re.fullmatch(r"[A-Za-z0-9_.-]+", value):
            raise ValidationError(
                "Username may contain only letters, numbers, dots, underscores, and hyphens."
            )
        field.data = value

    def validate_role(self, field):
        if field.data not in {"admin", "employee"}:
            raise ValidationError("Invalid role selected.")


class AdminResetPasswordForm(FlaskForm):
    new_password = PasswordField(
        "New Password",
        validators=[
            DataRequired(message="New password is required."),
            Length(min=8, max=128, message="Password must be at least 8 characters."),
        ],
        render_kw={"autocomplete": "new-password"},
    )

    confirm_password = PasswordField(
        "Confirm New Password",
        validators=[
            DataRequired(message="Please confirm the new password."),
            EqualTo("new_password", message="Passwords must match."),
        ],
        render_kw={"autocomplete": "new-password"},
    )

    submit = SubmitField("Reset Password")


class UserStatusForm(FlaskForm):
    is_active = BooleanField(
        "Active",
        validators=[Optional()],
    )

    submit = SubmitField("Update Status")