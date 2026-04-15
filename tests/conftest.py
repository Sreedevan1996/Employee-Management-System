from pathlib import Path

import pytest
from flask import Flask

from app.extensions import csrf, db, login_manager
from app.models import AuditLog, Department, Employee, User
from app.routes import register_blueprints
from app.utils.security import (
    apply_login_manager_settings,
    configure_security,
    register_security_headers,
)


TEMPLATE_CONTENT = """
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>{{ request.endpoint or "test-page" }}</title>
</head>
<body>
    {% with messages = get_flashed_messages(with_categories=true) %}
        {% if messages %}
            <div id="flashes">
                {% for category, message in messages %}
                    <div class="flash {{ category }}">{{ message }}</div>
                {% endfor %}
            </div>
        {% endif %}
    {% endwith %}

    <h1>{{ request.endpoint or "page" }}</h1>

    {% if employee %}
        <div id="employee">{{ employee.full_name if employee.full_name is defined else employee.id }}</div>
    {% endif %}

    {% if department %}
        <div id="department">{{ department.name }}</div>
    {% endif %}

    {% if employees %}
        {% for item in employees %}
            <div class="employee">{{ item.full_name }}</div>
        {% endfor %}
    {% endif %}

    {% if departments %}
        {% for item in departments %}
            <div class="department">{{ item.name }}</div>
        {% endfor %}
    {% endif %}

    {% if users %}
        {% for item in users %}
            <div class="user">{{ item.username }}</div>
        {% endfor %}
    {% endif %}

    {% if logs %}
        {% for item in logs %}
            <div class="log">{{ item.action }}</div>
        {% endfor %}
    {% endif %}

    {% if stats %}
        <div id="stats">{{ stats.employee_count }}</div>
    {% endif %}
</body>
</html>
"""


def _write_templates(template_root: Path) -> None:
    template_files = [
        "index.html",
        "auth/login.html",
        "admin/dashboard.html",
        "admin/users.html",
        "admin/department_list.html",
        "admin/department_form.html",
        "admin/audit_logs.html",
        "admin/employee_list.html",
        "admin/employee_form.html",
        "employee/dashboard.html",
        "employee/profile.html",
        "employee/profile_edit.html",
        "errors/403.html",
        "errors/404.html",
        "errors/500.html",
    ]

    for rel_path in template_files:
        file_path = template_root / rel_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(TEMPLATE_CONTENT, encoding="utf-8")


@pytest.fixture
def app(tmp_path):
    """
    Build an isolated Flask test app with its own SQLite database and
    minimal templates so route rendering works during tests.
    """
    db_path = tmp_path / "test_app.db"
    template_root = tmp_path / "templates"
    _write_templates(template_root)

    app = Flask(
        "employee_management_test_app",
        template_folder=str(template_root),
        instance_path=str(tmp_path / "instance"),
    )

    app.config.update(
        TESTING=True,
        SECRET_KEY="test-secret-key",
        SQLALCHEMY_DATABASE_URI=f"sqlite:///{db_path}",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        WTF_CSRF_ENABLED=False,
        SESSION_COOKIE_SECURE=False,
        REMEMBER_COOKIE_SECURE=False,
        SERVER_NAME="localhost.localdomain",
    )

    configure_security(app)
    app.config["SESSION_COOKIE_SECURE"] = False
    app.config["REMEMBER_COOKIE_SECURE"] = False
    app.config["WTF_CSRF_ENABLED"] = False

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    apply_login_manager_settings(login_manager)
    register_security_headers(app)
    register_blueprints(app)

    with app.app_context():
        db.create_all()

    yield app

    with app.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def admin_user(app):
    with app.app_context():
        user = User.create_admin(
            username="adminuser",
            email="admin@example.com",
            password="Admin1234",
        )
        db.session.add(user)
        db.session.commit()

        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "password": "Admin1234",
        }


@pytest.fixture
def employee_user(app):
    with app.app_context():
        user = User.create_employee_user(
            username="employeeuser",
            email="employee@example.com",
            password="Employee1234",
        )
        db.session.add(user)
        db.session.commit()

        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "password": "Employee1234",
        }


@pytest.fixture
def inactive_user(app):
    with app.app_context():
        user = User.create_employee_user(
            username="inactiveuser",
            email="inactive@example.com",
            password="Inactive1234",
        )
        user.is_active = False
        db.session.add(user)
        db.session.commit()

        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "password": "Inactive1234",
        }


@pytest.fixture
def department(app):
    with app.app_context():
        department = Department(
            name="Engineering",
            code="ENG",
            description="Engineering Department",
            manager_name="Sarah Connor",
            is_active=True,
        )
        db.session.add(department)
        db.session.commit()

        return {
            "id": department.id,
            "name": department.name,
            "code": department.code,
        }


@pytest.fixture
def employee_record(app, admin_user, employee_user, department):
    with app.app_context():
        employee = Employee(
            user_id=employee_user["id"],
            department_id=department["id"],
            employee_code="EMP100",
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            phone="+353871111111",
            job_title="Software Engineer",
            address="Dublin, Ireland",
            salary=65000,
            is_active=True,
            created_by=admin_user["id"],
            updated_by=admin_user["id"],
        )
        db.session.add(employee)
        db.session.commit()

        return {
            "id": employee.id,
            "employee_code": employee.employee_code,
            "email": employee.email,
            "user_id": employee.user_id,
        }


@pytest.fixture
def login_as(client):
    def _login(identifier: str, password: str, follow_redirects: bool = False):
        return client.post(
            "/auth/login",
            data={
                "identifier": identifier,
                "password": password,
                "remember_me": "y",
            },
            follow_redirects=follow_redirects,
        )

    return _login


@pytest.fixture
def logout_as(client):
    def _logout(follow_redirects: bool = False):
        return client.post("/auth/logout", follow_redirects=follow_redirects)

    return _logout


@pytest.fixture
def audit_log_count(app):
    def _count(action: str):
        with app.app_context():
            return AuditLog.query.filter_by(action=action).count()

    return _count