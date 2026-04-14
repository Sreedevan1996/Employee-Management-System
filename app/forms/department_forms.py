import re

from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional, ValidationError


def _strip_filter(value):
    return value.strip() if isinstance(value, str) else value


class DepartmentForm(FlaskForm):
    name = StringField(
        "Department Name",
        filters=[_strip_filter],
        validators=[
            DataRequired(message="Department name is required."),
            Length(min=2, max=100, message="Department name must be between 2 and 100 characters."),
        ],
        render_kw={"placeholder": "e.g. Human Resources"},
    )

    code = StringField(
        "Department Code",
        filters=[_strip_filter],
        validators=[
            DataRequired(message="Department code is required."),
            Length(min=2, max=20, message="Department code must be between 2 and 20 characters."),
        ],
        render_kw={"placeholder": "e.g. HR"},
    )

    description = TextAreaField(
        "Description",
        filters=[_strip_filter],
        validators=[
            Optional(),
            Length(max=500, message="Description cannot exceed 500 characters."),
        ],
        render_kw={"rows": 4},
    )

    manager_name = StringField(
        "Manager Name",
        filters=[_strip_filter],
        validators=[
            Optional(),
            Length(max=100, message="Manager name cannot exceed 100 characters."),
        ],
        render_kw={"placeholder": "e.g. Sarah O'Brien"},
    )

    is_active = BooleanField("Active", default=True)

    submit = SubmitField("Save Department")

    def validate_name(self, field):
        value = (field.data or "").strip()
        if not re.fullmatch(r"[A-Za-z0-9\s&'().,-]+", value):
            raise ValidationError("Department name contains invalid characters.")
        field.data = value

    def validate_code(self, field):
        value = (field.data or "").strip().upper()
        if not re.fullmatch(r"[A-Z0-9_-]+", value):
            raise ValidationError(
                "Department code may contain only letters, numbers, hyphens, and underscores."
            )
        field.data = value

    def validate_manager_name(self, field):
        if not field.data:
            return

        value = field.data.strip()
        if not re.fullmatch(r"[A-Za-z\s'.-]+", value):
            raise ValidationError("Manager name contains invalid characters.")
        field.data = value