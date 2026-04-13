from __future__ import annotations

from datetime import datetime
from typing import Optional

from flask_login import current_user, login_user, logout_user

from app.extensions import db
from app.models.user import User
from app.services import (
    AuthenticationError,
    AuthorizationError,
    ConflictError,
    NotFoundError,
    ValidationError,
)
from app.services.audit_service import AuditService


class AuthService:
    ALLOWED_ROLES = {"admin", "employee"}

    @staticmethod
    def _normalize_username(username: str) -> str:
        if not username or not username.strip():
            raise ValidationError("Username is required.")
        return username.strip()

    @staticmethod
    def _normalize_email(email: str) -> str:
        if not email or not email.strip():
            raise ValidationError("Email is required.")
        return email.strip().lower()

    @staticmethod
    def _validate_role(role: str) -> str:
        if not role or role.strip().lower() not in AuthService.ALLOWED_ROLES:
            raise ValidationError("Invalid role supplied.")
        return role.strip().lower()

    @staticmethod
    def _validate_password(password: str) -> str:
        if not password or len(password.strip()) < 8:
            raise ValidationError("Password must be at least 8 characters long.")
        return password.strip()

    @staticmethod
    def authenticate(identifier: str, password: str) -> User:
        """
        Validate username/email + password and return the user if valid.
        """
        if not identifier or not identifier.strip():
            raise ValidationError("Username or email is required.")

        if not password:
            raise ValidationError("Password is required.")

        identifier = identifier.strip()
        user = User.query.filter(
            (User.username == identifier) | (User.email == identifier.lower())
        ).first()

        if not user:
            raise AuthenticationError("Invalid credentials.")

        if not user.is_active:
            raise AuthenticationError("This account is inactive.")

        if not user.check_password(password):
            raise AuthenticationError("Invalid credentials.")

        return user

    @staticmethod
    def login(
        *,
        identifier: str,
        password: str,
        remember: bool = False,
        ip_address: Optional[str] = None,
    ) -> User:
        """
        Authenticate and log the user into the Flask session.
        """
        try:
            user = AuthService.authenticate(identifier, password)
            user.last_login_at = datetime.utcnow()
            db.session.commit()

            login_user(user, remember=remember)
            AuditService.log_login_success(user_id=user.id, ip_address=ip_address)
            return user

        except AuthenticationError:
            db.session.rollback()
            AuditService.log_login_failure(identifier=identifier, ip_address=ip_address)
            raise
        except Exception:
            db.session.rollback()
            AuditService.log_login_failure(identifier=identifier, ip_address=ip_address)
            raise

    @staticmethod
    def logout(ip_address: Optional[str] = None) -> None:
        """
        Log out the currently logged-in user.
        """
        if current_user.is_authenticated:
            user = current_user._get_current_object()
            AuditService.log_logout(user_id=user.id, ip_address=ip_address)
        logout_user()

    @staticmethod
    def create_user(
        *,
        username: str,
        email: str,
        password: str,
        role: str = "employee",
        actor_id: Optional[int] = None,
        ip_address: Optional[str] = None,
    ) -> User:
        """
        Create a new user account.
        """
        username = AuthService._normalize_username(username)
        email = AuthService._normalize_email(email)
        password = AuthService._validate_password(password)
        role = AuthService._validate_role(role)

        if User.query.filter_by(username=username).first():
            raise ConflictError("Username already exists.")

        if User.query.filter_by(email=email).first():
            raise ConflictError("Email already exists.")

        try:
            user = User(
                username=username,
                email=email,
                role=role,
                is_active=True,
            )
            user.set_password(password)

            db.session.add(user)
            db.session.flush()

            AuditService.log_event(
                action="CREATE_USER",
                user_id=actor_id,
                entity_type="USER",
                entity_id=user.id,
                status="SUCCESS",
                ip_address=ip_address,
                details=f"Created user account with role '{role}'.",
                commit=False,
            )

            db.session.commit()
            return user

        except Exception:
            db.session.rollback()
            if actor_id:
                AuditService.log_event(
                    action="CREATE_USER",
                    user_id=actor_id,
                    entity_type="USER",
                    entity_id=None,
                    status="FAILED",
                    ip_address=ip_address,
                    details=f"Failed to create user with email '{email}'.",
                    commit=True,
                )
            raise

    @staticmethod
    def get_user_by_id(user_id: int) -> User:
        user = db.session.get(User, user_id)
        if not user:
            raise NotFoundError("User not found.")
        return user

    @staticmethod
    def list_users(role: Optional[str] = None, active_only: bool = False) -> list[User]:
        query = User.query.order_by(User.created_at.desc())

        if role:
            query = query.filter(User.role == role.strip().lower())

        if active_only:
            query = query.filter(User.is_active.is_(True))

        return query.all()

    @staticmethod
    def set_user_active_status(
        *,
        user_id: int,
        is_active: bool,
        actor_id: Optional[int] = None,
        ip_address: Optional[str] = None,
    ) -> User:
        user = AuthService.get_user_by_id(user_id)

        try:
            user.is_active = bool(is_active)

            AuditService.log_event(
                action="UPDATE_USER_STATUS",
                user_id=actor_id,
                entity_type="USER",
                entity_id=user.id,
                status="SUCCESS",
                ip_address=ip_address,
                details=f"Set is_active={user.is_active} for user '{user.username}'.",
                commit=False,
            )

            db.session.commit()
            return user

        except Exception:
            db.session.rollback()
            raise

    @staticmethod
    def change_own_password(
        *,
        user_id: int,
        current_password: str,
        new_password: str,
        ip_address: Optional[str] = None,
    ) -> User:
        user = AuthService.get_user_by_id(user_id)

        if not user.check_password(current_password):
            raise AuthenticationError("Current password is incorrect.")

        new_password = AuthService._validate_password(new_password)

        try:
            user.set_password(new_password)

            AuditService.log_event(
                action="CHANGE_PASSWORD",
                user_id=user.id,
                entity_type="USER",
                entity_id=user.id,
                status="SUCCESS",
                ip_address=ip_address,
                details="User changed their password.",
                commit=False,
            )

            db.session.commit()
            return user

        except Exception:
            db.session.rollback()
            raise

    @staticmethod
    def admin_reset_password(
        *,
        target_user_id: int,
        new_password: str,
        actor_id: int,
        ip_address: Optional[str] = None,
    ) -> User:
        actor = AuthService.get_user_by_id(actor_id)
        if not actor.is_admin:
            raise AuthorizationError("Only admins can reset passwords.")

        user = AuthService.get_user_by_id(target_user_id)
        new_password = AuthService._validate_password(new_password)

        try:
            user.set_password(new_password)

            AuditService.log_event(
                action="ADMIN_RESET_PASSWORD",
                user_id=actor_id,
                entity_type="USER",
                entity_id=user.id,
                status="SUCCESS",
                ip_address=ip_address,
                details=f"Admin reset password for user '{user.username}'.",
                commit=False,
            )

            db.session.commit()
            return user

        except Exception:
            db.session.rollback()
            raise