from __future__ import annotations

from typing import Optional

from app.extensions import db
from app.models.audit_log import AuditLog


class AuditService:
    @staticmethod
    def log_event(
        *,
        action: str,
        user_id: Optional[int] = None,
        entity_type: Optional[str] = None,
        entity_id: Optional[int] = None,
        status: str = "SUCCESS",
        ip_address: Optional[str] = None,
        details: Optional[str] = None,
        commit: bool = True,
    ) -> AuditLog:
        """
        Create an audit log entry.

        Use commit=False when the caller wants to include the log in the same
        transaction as the main database operation.
        """
        log = AuditLog(
            user_id=user_id,
            action=action.strip(),
            entity_type=entity_type.strip() if entity_type else None,
            entity_id=entity_id,
            status=status.strip().upper(),
            ip_address=ip_address.strip() if ip_address else None,
            details=details.strip() if details else None,
        )
        db.session.add(log)

        if commit:
            db.session.commit()

        return log

    @staticmethod
    def log_login_success(user_id: int, ip_address: Optional[str] = None) -> AuditLog:
        return AuditService.log_event(
            action="LOGIN_SUCCESS",
            user_id=user_id,
            entity_type="USER",
            entity_id=user_id,
            status="SUCCESS",
            ip_address=ip_address,
            details="User logged in successfully.",
            commit=True,
        )

    @staticmethod
    def log_login_failure(
        identifier: str,
        ip_address: Optional[str] = None,
        user_id: Optional[int] = None,
    ) -> AuditLog:
        return AuditService.log_event(
            action="LOGIN_FAILURE",
            user_id=user_id,
            entity_type="USER",
            entity_id=user_id,
            status="FAILED",
            ip_address=ip_address,
            details=f"Failed login attempt for identifier: {identifier}",
            commit=True,
        )

    @staticmethod
    def log_logout(user_id: int, ip_address: Optional[str] = None) -> AuditLog:
        return AuditService.log_event(
            action="LOGOUT",
            user_id=user_id,
            entity_type="USER",
            entity_id=user_id,
            status="SUCCESS",
            ip_address=ip_address,
            details="User logged out.",
            commit=True,
        )

    @staticmethod
    def list_logs(
        *,
        user_id: Optional[int] = None,
        action: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100,
    ) -> list[AuditLog]:
        query = AuditLog.query.order_by(AuditLog.created_at.desc())

        if user_id is not None:
            query = query.filter(AuditLog.user_id == user_id)

        if action:
            query = query.filter(AuditLog.action == action.strip())

        if status:
            query = query.filter(AuditLog.status == status.strip().upper())

        return query.limit(limit).all()