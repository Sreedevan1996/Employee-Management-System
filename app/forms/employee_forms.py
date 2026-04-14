import re
from datetime import date

from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    DateField,
    DecimalField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.fields import EmailField
from wtforms.validators import (
    DataRequired,
    Email,
    Length,
    NumberRange,
    Optional,
    ValidationError,
)


def _strip_filter(value):
    return value.strip() if isinstance(value, str) else value


class EmployeeForm(FlaskForm):
    employee_code = StringField(
        "Employee Code",
        filters=[_strip_filter],
        validators=[
            DataRequired(message="Employee code is required."),
            Length(min=2, max=20, message="Employee code must be between 2 and 20 characters."),
        ],
        render_kw={"placeholder": "e.g. EMP001"},
    )

    first_name = StringField(
        "First Name",
        filters=[_strip_filter],
        validators=[
            DataRequired(message="First name is required."),
            Length(min=2, max=100, message="First name must be between 2 and 100 characters."),
        ],
    )

    last_name = StringField(
        "Last Name",
        filters=[_strip_filter],
        validators=[
            DataRequired(message="Last name is required."),
            Length(min=2, max=100, message="Last name must be between 2 and 100 characters."),
        ],
    )

    email = EmailField(
        "Email",
        filters=[_strip_filter],
        validators=[
            DataRequired(message="Email is required."),
            Email(message="Enter a valid email address."),
            Length(max=120, message="Email cannot exceed 120 characters."),
        ],
    )

    phone = StringField(
        "Phone",
        filters=[_strip_filter],
        validators=[
            Optional(),
            Length(max=20, message="Phone number cannot exceed 20 characters."),
        ],
        render_kw={"placeholder": "e.g. +353871234567"},
    )

    job_title = StringField(
        "Job Title",
        filters=[_strip_filter],
        validators=[
            DataRequired(message="Job title is required."),
            Length(min=2, max=100, message="Job title must be between 2 and 100 characters."),
        ],
    )

    address = TextAreaField(
        "Address",
        filters=[_strip_filter],
        validators=[
            Optional(),
            Length(max=255, message="Address cannot exceed 255 characters."),
        ],
        render_kw={"rows": 3},
    )

    salary = DecimalField(
        "Salary",
        validators=[
            Optional(),
            NumberRange(min=0, message="Salary cannot be negative."),
        ],
        places=2,
        rounding=None,
    )

    date_joined = DateField(
        "Date Joined",
        validators=[Optional()],
        format="%Y-%m-%d",
        default=date.today,
    )

    department_id = SelectField(
        "Department",
        coerce=int,
        validators=[Optional()],
        choices=[],
        default=0,
    )

    user_id = SelectField(
        "Linked User Account",
        coerce=int,
        validators=[Optional()],
        choices=[],
        default=0,
    )

    is_active = BooleanField("Active", default=True)

    submit = SubmitField("Save Employee")

    def validate_employee_code(self, field):
        value = (field.data or "").strip().upper()

        if not re.fullmatch(r"[A-Z0-9_-]+", value):
            raise ValidationError(
                "Employee code may contain only letters, numbers, hyphens, and underscores."
            )

        field.data = value

    def validate_first_name(self, field):
        value = (field.data or "").strip()
        if not re.fullmatch(r"[A-Za-z\s'-]+", value):
            raise ValidationError("First name contains invalid characters.")
        field.data = value

    def validate_last_name(self, field):
        value = (field.data or "").strip()
        if not re.fullmatch(r"[A-Za-z\s'-]+", value):
            raise ValidationError("Last name contains invalid characters.")
        field.data = value

    def validate_phone(self, field):
        if not field.data:
            return

        value = field.data.strip()
        if not re.fullmatch(r"[\d+\-\s()]+", value):
            raise ValidationError("Phone number contains invalid characters.")

        field.data = value

    def validate_department_id(self, field):
        if field.data is not None and field.data < 0:
            raise ValidationError("Invalid department selection.")

    def validate_user_id(self, field):
        if field.data is not None and field.data < 0:
            raise ValidationError("Invalid user selection.")


class ProfileForm(FlaskForm):
    phone = StringField(
        "Phone",
        filters=[_strip_filter],
        validators=[
            Optional(),
            Length(max=20, message="Phone number cannot exceed 20 characters."),
        ],
        render_kw={"placeholder": "e.g. +353871234567"},
    )

    address = TextAreaField(
        "Address",
        filters=[_strip_filter],
        validators=[
            Optional(),
            Length(max=255, message="Address cannot exceed 255 characters."),
        ],
        render_kw={"rows": 3},
    )

    submit = SubmitField("Update Profile")

    def validate_phone(self, field):
        if not field.data:
            return

        value = field.data.strip()
        if not re.fullmatch(r"[\d+\-\s()]+", value):
            raise ValidationError("Phone number contains invalid characters.")

        field.data = value