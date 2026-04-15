from app.extensions import db
from app.models.audit_log import AuditLog
from app.models.user import User
from app.services.employee_service import EmployeeService


def test_security_headers_are_present_on_responses(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"
    assert "Content-Security-Policy" in response.headers
    assert response.headers["Cache-Control"] == "no-store"


def test_password_is_hashed_and_not_stored_in_plain_text(app, admin_user):
    with app.app_context():
        user = db.session.get(User, admin_user["id"])

        assert user is not None
        assert user.password_hash != admin_user["password"]
        assert user.check_password(admin_user["password"]) is True


def test_sql_injection_style_login_attempt_does_not_authenticate_user_and_is_logged(
    client,
    app,
):
    response = client.post(
        "/auth/login",
        data={
            "identifier": "' OR 1=1 --",
            "password": "' OR 1=1 --",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200

    with client.session_transaction() as session:
        assert "_user_id" not in session

    with app.app_context():
        log = AuditLog.query.filter_by(action="LOGIN_FAILURE").first()
        assert log is not None
        assert "identifier" in (log.details or "").lower()


def test_employee_self_service_update_only_changes_allowed_fields(
    app,
    employee_user,
    employee_record,
):
    with app.app_context():
        before = EmployeeService.get_employee_by_id(employee_record["id"])
        original_job_title = before.job_title

        updated = EmployeeService.update_own_profile(
            user_id=employee_user["id"],
            data={
                "phone": "+353888888888",
                "address": "Updated Address",
                "job_title": "Chief Hacker",
            },
            ip_address="127.0.0.1",
        )

        assert updated.phone == "+353888888888"
        assert updated.address == "Updated Address"
        assert updated.job_title == original_job_title
        assert updated.updated_by == employee_user["id"]


def test_inactive_account_login_is_blocked(
    client,
    app,
    inactive_user,
):
    response = client.post(
        "/auth/login",
        data={
            "identifier": inactive_user["username"],
            "password": inactive_user["password"],
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"inactive" in response.data.lower()

    with client.session_transaction() as session:
        assert "_user_id" not in session

    with app.app_context():
        log = AuditLog.query.filter_by(action="LOGIN_FAILURE").first()
        assert log is not None