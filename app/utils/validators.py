import re
from decimal import Decimal, InvalidOperation
from typing import Optional


class ValidationUtils:
    USERNAME_PATTERN = re.compile(r"^[A-Za-z0-9_.-]{3,50}$")
    CODE_PATTERN = re.compile(r"^[A-Z0-9_-]{2,20}$")
    NAME_PATTERN = re.compile(r"^[A-Za-z\s'.-]{2,100}$")
    PHONE_PATTERN = re.compile(r"^[\d+\-\s()]{7,20}$")
    EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

    @staticmethod
    def sanitize_text(value: Optional[str], max_length: Optional[int] = None) -> Optional[str]:
        if value is None:
            return None

        cleaned = str(value).strip()

        if max_length is not None and len(cleaned) > max_length:
            raise ValueError(f"Value exceeds maximum length of {max_length}.")

        return cleaned or None

    @staticmethod
    def normalize_email(email: str) -> str:
        if not email or not str(email).strip():
            raise ValueError("Email is required.")

        cleaned = str(email).strip().lower()

        if not ValidationUtils.EMAIL_PATTERN.fullmatch(cleaned):
            raise ValueError("Invalid email address format.")

        return cleaned

    @staticmethod
    def normalize_code(code: str) -> str:
        if not code or not str(code).strip():
            raise ValueError("Code is required.")

        cleaned = str(code).strip().upper()

        if not ValidationUtils.CODE_PATTERN.fullmatch(cleaned):
            raise ValueError(
                "Code may contain only letters, numbers, hyphens, and underscores."
            )

        return cleaned

    @staticmethod
    def validate_username(username: str) -> str:
        if not username or not str(username).strip():
            raise ValueError("Username is required.")

        cleaned = str(username).strip()

        if not ValidationUtils.USERNAME_PATTERN.fullmatch(cleaned):
            raise ValueError(
                "Username may contain only letters, numbers, dots, underscores, and hyphens."
            )

        return cleaned

    @staticmethod
    def validate_name(name: str, field_name: str = "Name") -> str:
        if not name or not str(name).strip():
            raise ValueError(f"{field_name} is required.")

        cleaned = str(name).strip()

        if not ValidationUtils.NAME_PATTERN.fullmatch(cleaned):
            raise ValueError(f"{field_name} contains invalid characters.")

        return cleaned

    @staticmethod
    def validate_phone_number(phone: Optional[str]) -> Optional[str]:
        if phone is None or str(phone).strip() == "":
            return None

        cleaned = str(phone).strip()

        if not ValidationUtils.PHONE_PATTERN.fullmatch(cleaned):
            raise ValueError("Phone number contains invalid characters.")

        return cleaned

    @staticmethod
    def validate_password_strength(password: str) -> str:
        if not password or not str(password).strip():
            raise ValueError("Password is required.")

        cleaned = str(password).strip()

        if len(cleaned) < 8:
            raise ValueError("Password must be at least 8 characters long.")

        if not re.search(r"[A-Z]", cleaned):
            raise ValueError("Password must contain at least one uppercase letter.")

        if not re.search(r"[a-z]", cleaned):
            raise ValueError("Password must contain at least one lowercase letter.")

        if not re.search(r"\d", cleaned):
            raise ValueError("Password must contain at least one number.")

        return cleaned

    @staticmethod
    def parse_salary(value) -> Optional[Decimal]:
        if value in (None, "", "null"):
            return None

        try:
            salary = Decimal(str(value))
        except (InvalidOperation, ValueError) as exc:
            raise ValueError("Salary must be a valid number.") from exc

        if salary < 0:
            raise ValueError("Salary cannot be negative.")

        return salary

    @staticmethod
    def validate_role(role: str) -> str:
        if not role or not str(role).strip():
            raise ValueError("Role is required.")

        cleaned = str(role).strip().lower()

        if cleaned not in {"admin", "employee"}:
            raise ValueError("Role must be either 'admin' or 'employee'.")

        return cleaned


def sanitize_text(value: Optional[str], max_length: Optional[int] = None) -> Optional[str]:
    return ValidationUtils.sanitize_text(value=value, max_length=max_length)


def normalize_email(email: str) -> str:
    return ValidationUtils.normalize_email(email=email)


def normalize_code(code: str) -> str:
    return ValidationUtils.normalize_code(code=code)


def validate_password_strength(password: str) -> str:
    return ValidationUtils.validate_password_strength(password=password)


def validate_phone_number(phone: Optional[str]) -> Optional[str]:
    return ValidationUtils.validate_phone_number(phone=phone)