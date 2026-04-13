from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app.extensions import db, login_manager


class User(UserMixin, db.Model):
    __tablename__ = "users"

    __table_args__ = (
        db.CheckConstraint(
            "role IN ('admin', 'employee')",
            name="ck_users_role"
        ),
    )

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)

    password_hash = db.Column(db.String(255), nullable=False)

    role = db.Column(db.String(20), nullable=False, default="employee", index=True)
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    last_login_at = db.Column(db.DateTime, nullable=True)

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # One-to-one link for employee self-profile
    employee_profile = db.relationship(
        "Employee",
        back_populates="user_account",
        uselist=False,
        foreign_keys="Employee.user_id"
    )

    # Audit logs created by this user
    audit_logs = db.relationship(
        "AuditLog",
        back_populates="user",
        lazy="select"
    )

    # Track who created/updated employee records
    created_employees = db.relationship(
        "Employee",
        foreign_keys="Employee.created_by",
        back_populates="creator",
        lazy="select"
    )

    updated_employees = db.relationship(
        "Employee",
        foreign_keys="Employee.updated_by",
        back_populates="updater",
        lazy="select"
    )

    def set_password(self, raw_password: str) -> None:
        """
        Hash and store a password.
        """
        if not raw_password or len(raw_password.strip()) < 8:
            raise ValueError("Password must be at least 8 characters long.")

        self.password_hash = generate_password_hash(
            raw_password.strip(),
            method="pbkdf2:sha256"
        )

    def check_password(self, raw_password: str) -> bool:
        """
        Verify a plain-text password against the stored hash.
        """
        if not raw_password or not self.password_hash:
            return False
        return check_password_hash(self.password_hash, raw_password)

    def has_role(self, *roles: str) -> bool:
        """
        Check whether the user's role matches any allowed role.
        """
        return self.role in roles

    @property
    def is_admin(self) -> bool:
        return self.role == "admin"

    @property
    def is_employee(self) -> bool:
        return self.role == "employee"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "role": self.role,
            "is_active": self.is_active,
            "last_login_at": self.last_login_at.isoformat() if self.last_login_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self) -> str:
        return f"<User id={self.id} username={self.username} role={self.role}>"

    @staticmethod
    def create_admin(username: str, email: str, password: str) -> "User":
        user = User(
            username=username.strip(),
            email=email.strip().lower(),
            role="admin",
            is_active=True
        )
        user.set_password(password)
        return user

    @staticmethod
    def create_employee_user(username: str, email: str, password: str) -> "User":
        user = User(
            username=username.strip(),
            email=email.strip().lower(),
            role="employee",
            is_active=True
        )
        user.set_password(password)
        return user


@login_manager.user_loader
def load_user(user_id: str):
    """
    Flask-Login user loader.
    """
    try:
        return db.session.get(User, int(user_id))
    except (TypeError, ValueError):
        return None