from app.extensions import db
from app.models.audit_log import AuditLog
from app.models.employee import Employee


def test_admin_can_create_employee(
    client,
    app,
    admin_user,
    department,
    login_as,
):
    login_as(admin_user["username"], admin_user["password"])

    response = client.post(
        "/employees/create",
        data={
            "employee_code": "EMP200",
            "first_name": "Jane",
            "last_name": "Smith",
            "email": "jane.smith@example.com",
            "phone": "+353879999999",
            "job_title": "QA Analyst",
            "address": "Cork, Ireland",
            "salary": "55000.00",
            "date_joined": "2024-01-15",
            "department_id": str(department["id"]),
            "user_id": "0",
            "is_active": "y",
        },
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert "/employees/" in response.headers["Location"]

    with app.app_context():
        employee = Employee.query.filter_by(employee_code="EMP200").first()
        assert employee is not None
        assert employee.first_name == "Jane"
        assert employee.department_id == department["id"]

        log = AuditLog.query.filter_by(
            action="CREATE_EMPLOYEE",
            entity_type="EMPLOYEE",
            entity_id=employee.id,
        ).first()
        assert log is not None


def test_admin_can_update_employee(
    client,
    app,
    admin_user,
    department,
    employee_record,
    employee_user,
    login_as,
):
    login_as(admin_user["username"], admin_user["password"])

    response = client.post(
        f"/employees/{employee_record['id']}/edit",
        data={
            "employee_code": "EMP100",
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "phone": "+353870000000",
            "job_title": "Senior Software Engineer",
            "address": "Galway, Ireland",
            "salary": "70000.00",
            "date_joined": "2024-01-10",
            "department_id": str(department["id"]),
            "user_id": str(employee_user["id"]),
            "is_active": "y",
        },
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith(f"/employees/{employee_record['id']}")

    with app.app_context():
        employee = db.session.get(Employee, employee_record["id"])
        assert employee is not None
        assert employee.job_title == "Senior Software Engineer"
        assert employee.phone == "+353870000000"
        assert employee.address == "Galway, Ireland"

        log = AuditLog.query.filter_by(
            action="UPDATE_EMPLOYEE",
            entity_type="EMPLOYEE",
            entity_id=employee.id,
        ).first()
        assert log is not None


def test_admin_can_delete_employee(
    client,
    app,
    admin_user,
    employee_record,
    login_as,
):
    login_as(admin_user["username"], admin_user["password"])

    response = client.post(
        f"/employees/{employee_record['id']}/delete",
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/employees/")

    with app.app_context():
        deleted = db.session.get(Employee, employee_record["id"])
        assert deleted is None

        log = AuditLog.query.filter_by(
            action="DELETE_EMPLOYEE",
            entity_type="EMPLOYEE",
        ).first()
        assert log is not None