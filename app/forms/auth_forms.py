from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Length


def _strip_filter(value):
    return value.strip() if isinstance(value, str) else value


class LoginForm(FlaskForm):
    identifier = StringField(
        "Username or Email",
        filters=[_strip_filter],
        validators=[
            DataRequired(message="Username or email is required."),
            Length(min=3, max=120, message="Please enter a valid username or email."),
        ],
        render_kw={
            "placeholder": "Enter username or email",
            "autocomplete": "username",
        },
    )

    password = PasswordField(
        "Password",
        validators=[
            DataRequired(message="Password is required."),
            Length(min=8, max=128, message="Password must be at least 8 characters."),
        ],
        render_kw={
            "placeholder": "Enter your password",
            "autocomplete": "current-password",
        },
    )

    remember_me = BooleanField("Remember Me")

    submit = SubmitField("Login")