import os
from datetime import date

from app import create_app
from app.extensions import db
from app.models import Department, Employee, User


def get_or_create_department(name: str, code: str, description: str, manager_name: str) -> Department:
    department = Department.query.filter_by(code=code).first()

    if department:
        department.name = name
        department.description = description
        department.manager_name = manager_name
        department.is_active = True
        return department

    department = Department(
        name=name,
        code=code,
        description=description,
        manager_name=manager_name,
        is_active=True,
    )
    db.session.add(department)
    db.session.flush()
    return department


def get_or_create_user(username: str, email: str, password: str, role: str) -> User:
    user = User.query.filter_by(email=email.lower()).first()

    if user:
        user.username = username
        user.email = email.lower()
        user.role = role
        user.is_active = True
        return user

    if role == "admin":
        user = User.create_admin(username=username, email=email, password=password)
    else:
        user = User.create_employee_user(username=username, email=email, password=password)

    db.session.add(user)
    db.session.flush()
    return user


def get_or_create_employee(
    *,
    user_id: int,
    department_id: int,
    employee_code: str,
    first_name: str,
    last_name: str,
    email: str,
    phone: str,
    job_title: str,
    address: str,
    salary: float,
    created_by: int,
) -> Employee:
    employee = Employee.query.filter_by(employee_code=employee_code).first()

    if employee:
        employee.user_id = user_id
        employee.department_id = department_id
        employee.first_name = first_name
        employee.last_name = last_name
        employee.email = email.lower()
        employee.phone = phone
        employee.job_title = job_title
        employee.address = address
        employee.salary = salary
        employee.is_active = True
        employee.updated_by = created_by
        return employee

    employee = Employee(
        user_id=user_id,
        department_id=department_id,
        employee_code=employee_code,
        first_name=first_name,
        last_name=last_name,
        email=email.lower(),
        phone=phone,
        job_title=job_title,
        address=address,
        salary=salary,
        date_joined=date.today(),
        is_active=True,
        created_by=created_by,
        updated_by=created_by,
    )
    db.session.add(employee)
    db.session.flush()
    return employee


def seed():
    print("Seeding database...")

    # Departments
    engineering = get_or_create_department(
        name="Engineering",
        code="ENG",
        description="Handles software development and maintenance.",
        manager_name="Sarah Connor",
    )

    hr = get_or_create_department(
        name="Human Resources",
        code="HR",
        description="Handles hiring, onboarding, and people operations.",
        manager_name="Jane Foster",
    )

    finance = get_or_create_department(
        name="Finance",
        code="FIN",
        description="Handles payroll, budgeting, and finance operations.",
        manager_name="Bruce Wayne",
    )

    # Users
    admin_user = get_or_create_user(
        username="admin",
        email="admin@example.com",
        password="Admin1234",
        role="admin",
    )

    employee_user = get_or_create_user(
        username="employee1",
        email="employee1@example.com",
        password="Employee1234",
        role="employee",
    )

    employee_user_2 = get_or_create_user(
        username="employee2",
        email="employee2@example.com",
        password="Employee1234",
        role="employee",
    )

    # Employees
    get_or_create_employee(
        user_id=employee_user.id,
        department_id=engineering.id,
        employee_code="EMP001",
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        phone="+353871111111",
        job_title="Software Engineer",
        address="Dublin, Ireland",
        salary=65000,
        created_by=admin_user.id,
    )

    get_or_create_employee(
        user_id=employee_user_2.id,
        department_id=hr.id,
        employee_code="EMP002",
        first_name="Emily",
        last_name="Smith",
        email="emily.smith@example.com",
        phone="+353872222222",
        job_title="HR Specialist",
        address="Cork, Ireland",
        salary=50000,
        created_by=admin_user.id,
    )

    db.session.commit()
    print("Database seeded successfully.")
    print("Demo credentials:")
    print("  Admin    -> admin / Admin1234")
    print("  Employee -> employee1 / Employee1234")
    print("  Employee -> employee2 / Employee1234")


if __name__ == "__main__":
    config_name = os.getenv("FLASK_CONFIG", "development")
    app = create_app(config_name)

    with app.app_context():
        seed()