from datetime import date, datetime

from app.extensions import db


class Employee(db.Model):
    __tablename__ = "employees"

    __table_args__ = (
        db.CheckConstraint("salary >= 0", name="ck_employees_salary_non_negative"),
    )

    id = db.Column(db.Integer, primary_key=True)

    # Optional: link login account to employee profile
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="SET NULL"),
        unique=True,
        nullable=True,
        index=True
    )

    department_id = db.Column(
        db.Integer,
        db.ForeignKey("departments.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    employee_code = db.Column(db.String(20), unique=True, nullable=False, index=True)

    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)

    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(20), nullable=True)

    job_title = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(255), nullable=True)

    salary = db.Column(db.Numeric(10, 2), nullable=True)
    date_joined = db.Column(db.Date, nullable=False, default=date.today)

    is_active = db.Column(db.Boolean, nullable=False, default=True)

    created_by = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )

    updated_by = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # Relationships
    user_account = db.relationship(
        "User",
        back_populates="employee_profile",
        foreign_keys=[user_id]
    )

    department = db.relationship(
        "Department",
        back_populates="employees"
    )

    creator = db.relationship(
        "User",
        foreign_keys=[created_by],
        back_populates="created_employees"
    )

    updater = db.relationship(
        "User",
        foreign_keys=[updated_by],
        back_populates="updated_employees"
    )

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "department_id": self.department_id,
            "employee_code": self.employee_code,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "full_name": self.full_name,
            "email": self.email,
            "phone": self.phone,
            "job_title": self.job_title,
            "address": self.address,
            "salary": float(self.salary) if self.salary is not None else None,
            "date_joined": self.date_joined.isoformat() if self.date_joined else None,
            "is_active": self.is_active,
            "created_by": self.created_by,
            "updated_by": self.updated_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self) -> str:
        return f"<Employee id={self.id} code={self.employee_code} name={self.full_name}>"