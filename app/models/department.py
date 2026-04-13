from datetime import datetime

from app.extensions import db


class Department(db.Model):
    __tablename__ = "departments"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), unique=True, nullable=False, index=True)
    code = db.Column(db.String(20), unique=True, nullable=False, index=True)

    description = db.Column(db.Text, nullable=True)
    manager_name = db.Column(db.String(100), nullable=True)

    is_active = db.Column(db.Boolean, nullable=False, default=True)

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    employees = db.relationship(
        "Employee",
        back_populates="department",
        lazy="select"
    )

    @property
    def employee_count(self) -> int:
        return len(self.employees)

    def to_dict(self, include_employees: bool = False) -> dict:
        data = {
            "id": self.id,
            "name": self.name,
            "code": self.code,
            "description": self.description,
            "manager_name": self.manager_name,
            "is_active": self.is_active,
            "employee_count": self.employee_count,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

        if include_employees:
            data["employees"] = [employee.to_dict() for employee in self.employees]

        return data

    def __repr__(self) -> str:
        return f"<Department id={self.id} code={self.code} name={self.name}>"