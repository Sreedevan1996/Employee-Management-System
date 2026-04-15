from app.extensions import db
from app.models.audit_log import AuditLog
from app.models.department import Department


def test_admin_can_create_department(
    client,
    app,
    admin_user,
    login_as,
):
    login_as(admin_user["username"], admin_user["password"])

    response = client.post(
        "/admin/departments/create",
        data={
            "name": "Finance",
            "code": "FIN",
            "description": "Finance Department",
            "manager_name": "Alice Johnson",
            "is_active": "y",
        },
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/admin/departments")

    with app.app_context():
        department = Department.query.filter_by(code="FIN").first()
        assert department is not None
        assert department.name == "Finance"

        log = AuditLog.query.filter_by(
            action="CREATE_DEPARTMENT",
            entity_type="DEPARTMENT",
            entity_id=department.id,
        ).first()
        assert log is not None


def test_admin_can_update_department(
    client,
    app,
    admin_user,
    department,
    login_as,
):
    login_as(admin_user["username"], admin_user["password"])

    response = client.post(
        f"/admin/departments/{department['id']}/edit",
        data={
            "name": "Engineering Operations",
            "code": "ENGOPS",
            "description": "Updated Department Description",
            "manager_name": "Ellen Ripley",
            "is_active": "y",
        },
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/admin/departments")

    with app.app_context():
        updated = db.session.get(Department, department["id"])
        assert updated is not None
        assert updated.name == "Engineering Operations"
        assert updated.code == "ENGOPS"

        log = AuditLog.query.filter_by(
            action="UPDATE_DEPARTMENT",
            entity_type="DEPARTMENT",
            entity_id=updated.id,
        ).first()
        assert log is not None


def test_admin_can_delete_department_when_no_employees_are_assigned(
    client,
    app,
    admin_user,
    department,
    login_as,
):
    login_as(admin_user["username"], admin_user["password"])

    response = client.post(
        f"/admin/departments/{department['id']}/delete",
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/admin/departments")

    with app.app_context():
        deleted = db.session.get(Department, department["id"])
        assert deleted is None

        log = AuditLog.query.filter_by(
            action="DELETE_DEPARTMENT",
            entity_type="DEPARTMENT",
        ).first()
        assert log is not None


def test_department_delete_is_blocked_when_employees_are_assigned(
    client,
    app,
    admin_user,
    department,
    employee_record,
    login_as,
):
    login_as(admin_user["username"], admin_user["password"])

    response = client.post(
        f"/admin/departments/{department['id']}/delete",
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Cannot delete department while employees are assigned to it." in response.data

    with app.app_context():
        existing = db.session.get(Department, department["id"])
        assert existing is not None