from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import Optional

from sqlalchemy import or_

from app.extensions import db
from app.models.department import Department
from app.models.employee import Employee
from app.models.user import User
from app.services import ConflictError, NotFoundError, ValidationError
from app.services.audit_service import AuditService


class EmployeeService:
    REQUIRED_FIELDS_ON_CREATE = {
        "employee_code",
        "first_name",
        "last_name",
        "email",
        "job_title",
    }

    @staticmethod
    def _clean_string(value: Optional[str], field_name: str, required: bool = False) -> Optional[str]:
        if value is None:
            if required:
                raise ValidationError(f"{field_name} is required.")
            return None

        cleaned = str(value).strip()

        if required and not cleaned:
            raise ValidationError(f"{field_name} is required.")

        return cleaned or None

    @staticmethod
    def _normalize_email(email: str) -> str:
        cleaned = EmployeeService._clean_string(email, "Email", required=True)
        return cleaned.lower()

    @staticmethod
    def _normalize_employee_code(employee_code: str) -> str:
        cleaned = EmployeeService._clean_string(employee_code, "Employee code", required=True)
        return cleaned.upper()

    @staticmethod
    def _parse_date_joined(value) -> date:
        if value is None or value == "":
            return date.today()

        if isinstance(value, date):
            return value

        try:
            return datetime.strptime(str(value), "%Y-%m-%d").date()
        except ValueError as exc:
            raise ValidationError("date_joined must be in YYYY-MM-DD format.") from exc

    @staticmethod
    def _parse_salary(value) -> Optional[Decimal]:
        if value in (None, "", "null"):
            return None

        try:
            salary = Decimal(str(value))
        except (InvalidOperation, ValueError) as exc:
            raise ValidationError("Salary must be a valid number.") from exc

        if salary < 0:
            raise ValidationError("Salary cannot be negative.")

        return salary

    @staticmethod
    def _validate_department(department_id: Optional[int]) -> Optional[int]:
        if department_id in (None, "", 0, "0"):
            return None

        department = db.session.get(Department, int(department_id))
        if not department:
            raise ValidationError("Selected department does not exist.")

        return department.id

    @staticmethod
    def _validate_user_link(user_id: Optional[int], current_employee_id: Optional[int] = None) -> Optional[int]:
        if user_id in (None, "", 0, "0"):
            return None

        user = db.session.get(User, int(user_id))
        if not user:
            raise ValidationError("Selected user account does not exist.")

        if user.role != "employee":
            raise ValidationError("Only employee user accounts can be linked to employee profiles.")

        linked_employee = Employee.query.filter(Employee.user_id == user.id).first()
        if linked_employee and linked_employee.id != current_employee_id:
            raise ConflictError("This user account is already linked to another employee profile.")

        return user.id

    @staticmethod
    def _validate_uniqueness(
        *,
        employee_code: str,
        email: str,
        employee_id: Optional[int] = None,
    ) -> None:
        existing_code = Employee.query.filter(
            Employee.employee_code == employee_code,
            Employee.id != employee_id if employee_id else True,
        ).first()
        if existing_code:
            raise ConflictError("Employee code already exists.")

        existing_email = Employee.query.filter(
            Employee.email == email,
            Employee.id != employee_id if employee_id else True,
        ).first()
        if existing_email:
            raise ConflictError("Employee email already exists.")

    @staticmethod
    def _prepare_payload(data: dict, *, partial: bool = False) -> dict:
        if not isinstance(data, dict):
            raise ValidationError("Invalid employee payload.")

        if not partial:
            missing = [
                field for field in EmployeeService.REQUIRED_FIELDS_ON_CREATE
                if not data.get(field)
            ]
            if missing:
                raise ValidationError(f"Missing required fields: {', '.join(missing)}")

        prepared = {}

        if "employee_code" in data or not partial:
            prepared["employee_code"] = EmployeeService._normalize_employee_code(
                data.get("employee_code")
            )

        if "first_name" in data or not partial:
            prepared["first_name"] = EmployeeService._clean_string(
                data.get("first_name"), "First name", required=not partial
            )

        if "last_name" in data or not partial:
            prepared["last_name"] = EmployeeService._clean_string(
                data.get("last_name"), "Last name", required=not partial
            )

        if "email" in data or not partial:
            prepared["email"] = EmployeeService._normalize_email(data.get("email"))

        if "phone" in data:
            prepared["phone"] = EmployeeService._clean_string(data.get("phone"), "Phone")

        if "job_title" in data or not partial:
            prepared["job_title"] = EmployeeService._clean_string(
                data.get("job_title"), "Job title", required=not partial
            )

        if "address" in data:
            prepared["address"] = EmployeeService._clean_string(data.get("address"), "Address")

        if "salary" in data:
            prepared["salary"] = EmployeeService._parse_salary(data.get("salary"))

        if "date_joined" in data or not partial:
            prepared["date_joined"] = EmployeeService._parse_date_joined(data.get("date_joined"))

        if "is_active" in data:
            prepared["is_active"] = bool(data.get("is_active"))

        if "department_id" in data:
            prepared["department_id"] = EmployeeService._validate_department(data.get("department_id"))

        if "user_id" in data:
            prepared["user_id"] = data.get("user_id")

        return prepared

    @staticmethod
    def get_employee_by_id(employee_id: int) -> Employee:
        employee = db.session.get(Employee, employee_id)
        if not employee:
            raise NotFoundError("Employee not found.")
        return employee

    @staticmethod
    def get_employee_by_user_id(user_id: int) -> Employee:
        employee = Employee.query.filter_by(user_id=user_id).first()
        if not employee:
            raise NotFoundError("Employee profile not found for this user.")
        return employee

    @staticmethod
    def list_employees(
        *,
        search: Optional[str] = None,
        department_id: Optional[int] = None,
        active_only: bool = False,
    ) -> list[Employee]:
        query = Employee.query.order_by(Employee.created_at.desc())

        if search and search.strip():
            term = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    Employee.first_name.ilike(term),
                    Employee.last_name.ilike(term),
                    Employee.email.ilike(term),
                    Employee.employee_code.ilike(term),
                    Employee.job_title.ilike(term),
                )
            )

        if department_id:
            query = query.filter(Employee.department_id == department_id)

        if active_only:
            query = query.filter(Employee.is_active.is_(True))

        return query.all()

    @staticmethod
    def create_employee(
        *,
        data: dict,
        actor_id: Optional[int] = None,
        ip_address: Optional[str] = None,
    ) -> Employee:
        prepared = EmployeeService._prepare_payload(data, partial=False)

        user_id = EmployeeService._validate_user_link(prepared.get("user_id"))
        prepared["user_id"] = user_id

        EmployeeService._validate_uniqueness(
            employee_code=prepared["employee_code"],
            email=prepared["email"],
        )

        try:
            employee = Employee(
                user_id=prepared.get("user_id"),
                department_id=prepared.get("department_id"),
                employee_code=prepared["employee_code"],
                first_name=prepared["first_name"],
                last_name=prepared["last_name"],
                email=prepared["email"],
                phone=prepared.get("phone"),
                job_title=prepared["job_title"],
                address=prepared.get("address"),
                salary=prepared.get("salary"),
                date_joined=prepared["date_joined"],
                is_active=prepared.get("is_active", True),
                created_by=actor_id,
                updated_by=actor_id,
            )

            db.session.add(employee)
            db.session.flush()

            AuditService.log_event(
                action="CREATE_EMPLOYEE",
                user_id=actor_id,
                entity_type="EMPLOYEE",
                entity_id=employee.id,
                status="SUCCESS",
                ip_address=ip_address,
                details=f"Created employee '{employee.full_name}' with code '{employee.employee_code}'.",
                commit=False,
            )

            db.session.commit()
            return employee

        except Exception:
            db.session.rollback()
            raise

    @staticmethod
    def update_employee(
        *,
        employee_id: int,
        data: dict,
        actor_id: Optional[int] = None,
        ip_address: Optional[str] = None,
    ) -> Employee:
        employee = EmployeeService.get_employee_by_id(employee_id)
        prepared = EmployeeService._prepare_payload(data, partial=True)

        new_employee_code = prepared.get("employee_code", employee.employee_code)
        new_email = prepared.get("email", employee.email)

        EmployeeService._validate_uniqueness(
            employee_code=new_employee_code,
            email=new_email,
            employee_id=employee.id,
        )

        if "user_id" in prepared:
            prepared["user_id"] = EmployeeService._validate_user_link(
                prepared.get("user_id"),
                current_employee_id=employee.id,
            )

        try:
            for field, value in prepared.items():
                setattr(employee, field, value)

            employee.updated_by = actor_id

            AuditService.log_event(
                action="UPDATE_EMPLOYEE",
                user_id=actor_id,
                entity_type="EMPLOYEE",
                entity_id=employee.id,
                status="SUCCESS",
                ip_address=ip_address,
                details=f"Updated employee '{employee.full_name}'.",
                commit=False,
            )

            db.session.commit()
            return employee

        except Exception:
            db.session.rollback()
            raise

    @staticmethod
    def delete_employee(
        *,
        employee_id: int,
        actor_id: Optional[int] = None,
        ip_address: Optional[str] = None,
    ) -> None:
        employee = EmployeeService.get_employee_by_id(employee_id)
        employee_name = employee.full_name

        try:
            AuditService.log_event(
                action="DELETE_EMPLOYEE",
                user_id=actor_id,
                entity_type="EMPLOYEE",
                entity_id=employee.id,
                status="SUCCESS",
                ip_address=ip_address,
                details=f"Deleted employee '{employee_name}'.",
                commit=False,
            )

            db.session.delete(employee)
            db.session.commit()

        except Exception:
            db.session.rollback()
            raise

    @staticmethod
    def update_own_profile(
        *,
        user_id: int,
        data: dict,
        ip_address: Optional[str] = None,
    ) -> Employee:
        """
        Restricted update for employee self-service.
        Only limited fields are allowed.
        """
        employee = EmployeeService.get_employee_by_user_id(user_id)

        allowed_fields = {"phone", "address"}
        filtered_data = {key: value for key, value in data.items() if key in allowed_fields}

        if not filtered_data:
            raise ValidationError("No allowed profile fields were provided.")

        prepared = EmployeeService._prepare_payload(filtered_data, partial=True)

        try:
            for field, value in prepared.items():
                setattr(employee, field, value)

            employee.updated_by = user_id

            AuditService.log_event(
                action="UPDATE_OWN_PROFILE",
                user_id=user_id,
                entity_type="EMPLOYEE",
                entity_id=employee.id,
                status="SUCCESS",
                ip_address=ip_address,
                details=f"Employee '{employee.full_name}' updated their own profile.",
                commit=False,
            )

            db.session.commit()
            return employee

        except Exception:
            db.session.rollback()
            raise