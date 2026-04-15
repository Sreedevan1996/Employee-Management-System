from app.extensions import db
from app.models.audit_log import AuditLog
from app.models.user import User


def test_admin_login_success_redirects_to_admin_dashboard(
    client,
    app,
    admin_user,
    login_as,
):
    response = login_as(admin_user["username"], admin_user["password"])

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/admin/dashboard")

    with client.session_transaction() as session:
        assert session.get("_user_id") == str(admin_user["id"])

    with app.app_context():
        user = db.session.get(User, admin_user["id"])
        assert user is not None
        assert user.last_login_at is not None

        log = AuditLog.query.filter_by(
            action="LOGIN_SUCCESS",
            user_id=admin_user["id"],
        ).first()
        assert log is not None


def test_employee_login_success_redirects_to_profile_dashboard(
    client,
    app,
    employee_user,
    login_as,
):
    response = login_as(employee_user["username"], employee_user["password"])

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/profile/dashboard")

    with client.session_transaction() as session:
        assert session.get("_user_id") == str(employee_user["id"])

    with app.app_context():
        log = AuditLog.query.filter_by(
            action="LOGIN_SUCCESS",
            user_id=employee_user["id"],
        ).first()
        assert log is not None


def test_invalid_login_does_not_authenticate_user_and_logs_failure(
    client,
    app,
    admin_user,
    login_as,
):
    response = login_as(admin_user["username"], "WrongPassword123", follow_redirects=True)

    assert response.status_code == 200
    assert b"Invalid credentials." in response.data

    with client.session_transaction() as session:
        assert "_user_id" not in session

    with app.app_context():
        log = AuditLog.query.filter_by(action="LOGIN_FAILURE").first()
        assert log is not None
        assert "adminuser" in (log.details or "")


def test_inactive_user_cannot_log_in(
    client,
    app,
    inactive_user,
    login_as,
):
    response = login_as(inactive_user["username"], inactive_user["password"], follow_redirects=True)

    assert response.status_code == 200
    assert b"inactive" in response.data.lower()

    with client.session_transaction() as session:
        assert "_user_id" not in session

    with app.app_context():
        log = AuditLog.query.filter_by(action="LOGIN_FAILURE").first()
        assert log is not None


def test_logout_clears_session_and_creates_audit_log(
    client,
    app,
    admin_user,
    login_as,
    logout_as,
):
    login_as(admin_user["username"], admin_user["password"])

    response = logout_as()

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/auth/login")

    with client.session_transaction() as session:
        assert "_user_id" not in session

    with app.app_context():
        log = AuditLog.query.filter_by(
            action="LOGOUT",
            user_id=admin_user["id"],
        ).first()
        assert log is not None