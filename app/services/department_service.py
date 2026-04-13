from __future__ import annotations

from typing import Optional

from app.extensions import db
from app.models.department import Department
from app.services import ConflictError, NotFoundError, ValidationError
from app.services.audit_service import AuditService


class DepartmentService:
    @staticmethod
    def _normalize_name(name: str) -> str:
        if not name or not name.strip():
            raise ValidationError("Department name is required.")
        return name.strip()

    @staticmethod
    def _normalize_code(code: str) -> str:
        if not code or not code.strip():
            raise ValidationError("Department code is required.")
        return code.strip().upper()

    @staticmethod
    def create_department(
        *,
        name: str,
        code: str,
        description: Optional[str] = None,
        manager_name: Optional[str] = None,
        actor_id: Optional[int] = None,
        ip_address: Optional[str] = None,
    ) -> Department:
        name = DepartmentService._normalize_name(name)
        code = DepartmentService._normalize_code(code)

        if Department.query.filter_by(name=name).first():
            raise ConflictError("Department name already exists.")

        if Department.query.filter_by(code=code).first():
            raise ConflictError("Department code already exists.")

        try:
            department = Department(
                name=name,
                code=code,
                description=description.strip() if description else None,
                manager_name=manager_name.strip() if manager_name else None,
                is_active=True,
            )

            db.session.add(department)
            db.session.flush()

            AuditService.log_event(
                action="CREATE_DEPARTMENT",
                user_id=actor_id,
                entity_type="DEPARTMENT",
                entity_id=department.id,
                status="SUCCESS",
                ip_address=ip_address,
                details=f"Created department '{department.name}'.",
                commit=False,
            )

            db.session.commit()
            return department

        except Exception:
            db.session.rollback()
            raise

    @staticmethod
    def get_department_by_id(department_id: int) -> Department:
        department = db.session.get(Department, department_id)
        if not department:
            raise NotFoundError("Department not found.")
        return department

    @staticmethod
    def list_departments(active_only: bool = False) -> list[Department]:
        query = Department.query.order_by(Department.name.asc())

        if active_only:
            query = query.filter(Department.is_active.is_(True))

        return query.all()

    @staticmethod
    def update_department(
        *,
        department_id: int,
        name: str,
        code: str,
        description: Optional[str] = None,
        manager_name: Optional[str] = None,
        is_active: Optional[bool] = None,
        actor_id: Optional[int] = None,
        ip_address: Optional[str] = None,
    ) -> Department:
        department = DepartmentService.get_department_by_id(department_id)

        name = DepartmentService._normalize_name(name)
        code = DepartmentService._normalize_code(code)

        existing_by_name = Department.query.filter(
            Department.name == name,
            Department.id != department.id
        ).first()
        if existing_by_name:
            raise ConflictError("Another department already uses this name.")

        existing_by_code = Department.query.filter(
            Department.code == code,
            Department.id != department.id
        ).first()
        if existing_by_code:
            raise ConflictError("Another department already uses this code.")

        try:
            department.name = name
            department.code = code
            department.description = description.strip() if description else None
            department.manager_name = manager_name.strip() if manager_name else None

            if is_active is not None:
                department.is_active = bool(is_active)

            AuditService.log_event(
                action="UPDATE_DEPARTMENT",
                user_id=actor_id,
                entity_type="DEPARTMENT",
                entity_id=department.id,
                status="SUCCESS",
                ip_address=ip_address,
                details=f"Updated department '{department.name}'.",
                commit=False,
            )

            db.session.commit()
            return department

        except Exception:
            db.session.rollback()
            raise

    @staticmethod
    def delete_department(
        *,
        department_id: int,
        actor_id: Optional[int] = None,
        ip_address: Optional[str] = None,
    ) -> None:
        department = DepartmentService.get_department_by_id(department_id)

        if department.employees:
            raise ConflictError(
                "Cannot delete department while employees are assigned to it."
            )

        try:
            AuditService.log_event(
                action="DELETE_DEPARTMENT",
                user_id=actor_id,
                entity_type="DEPARTMENT",
                entity_id=department.id,
                status="SUCCESS",
                ip_address=ip_address,
                details=f"Deleted department '{department.name}'.",
                commit=False,
            )

            db.session.delete(department)
            db.session.commit()

        except Exception:
            db.session.rollback()
            raise