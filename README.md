# Employee Management System

A secure, role-based **Employee Management System (EMS)** developed using **Flask**, **SQLAlchemy**, and **Flask-Login**. The application is designed to support administrative management of employees, departments, user accounts, and audit records within a structured web-based environment. Its primary security focus is the implementation of secure authentication, authorization, input validation, CSRF protection, safe session handling, security headers, and audit logging.

This project was developed for educational purposes as part of a secure web development assessment. It demonstrates how functional business requirements can be combined with security controls throughout design, implementation, and testing.

---

## Project Overview

The system provides two distinct user roles:

- **Admin**
  - Manage employees
  - Manage departments
  - Create user accounts
  - View audit logs
- **Employee**
  - Log in securely
  - View own profile
  - Update limited personal details

The application implements:

- CRUD operations for employees and departments
- Role-based access control
- Audit logging for security-sensitive actions
- A modular Flask architecture
- Automated functional and security-focused testing

---

## Features and Security Objectives

### Core Functional Features

- Secure login and logout
- Admin dashboard
- Employee CRUD management
- Department CRUD management
- User account creation and status management
- Employee self-service profile view and edit
- Audit log viewing for administrators

### Security Objectives

The main security objective of this project is to ensure that the application is not only functionally complete but also protected against common web application risks.

Implemented security improvements include:

- **Password Hashing**
  - Passwords are hashed before storage using Werkzeug’s secure password hashing utilities.
- **Authentication**
  - Only authenticated users can access protected parts of the system.
- **Authorization**
  - Admin-only routes are protected through role-based decorators.
- **CSRF Protection**
  - State-changing forms are protected using Flask-WTF CSRF tokens.
- **Server-Side Input Validation**
  - Forms and service-layer validation are used to reject invalid or malicious input.
- **SQL Injection Risk Reduction**
  - SQLAlchemy ORM is used instead of raw SQL queries.
- **Secure Session Handling**
  - Session and remember cookies are configured with secure settings.
- **Security Headers**
  - Headers such as `X-Frame-Options`, `X-Content-Type-Options`, and `Content-Security-Policy` are applied.
- **Audit Logging**
  - Login events and key administrative actions are logged.
- **Controlled Error Handling**
  - Custom 403, 404, and 500 error pages reduce information leakage.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3, Flask |
| ORM / Data Access | SQLAlchemy, Flask-SQLAlchemy, Flask-Migrate |
| Authentication | Flask-Login, Werkzeug |
| Forms / Validation | Flask-WTF, WTForms, email-validator |
| Frontend | HTML, CSS, JavaScript, Jinja2 |
| Database | SQLite (development), PostgreSQL-ready configuration |
| Testing | Pytest, pytest-cov |
| Security Review | Bandit, pip-audit |

---

## Project Structure

```text
Employee-Management-System/
├── app/
│   ├── __init__.py              # Application factory and app initialization
│   ├── config.py                # Environment-specific configuration classes
│   ├── extensions.py            # Flask extension setup (db, migrate, login, csrf)
│   │
│   ├── models/                  # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── user.py              # User accounts and role information
│   │   ├── employee.py          # Employee entity and profile details
│   │   ├── department.py        # Department entity
│   │   └── audit_log.py         # Audit log entity
│   │
│   ├── services/                # Business logic layer
│   │   ├── __init__.py
│   │   ├── auth_service.py      # Authentication and user-related operations
│   │   ├── employee_service.py  # Employee CRUD and self-service logic
│   │   ├── department_service.py# Department CRUD logic
│   │   └── audit_service.py     # Audit logging logic
│   │
│   ├── routes/                  # Blueprint routes/controllers
│   │   ├── __init__.py
│   │   ├── auth.py              # Login and logout routes
│   │   ├── main.py              # Home/index routes
│   │   ├── admin.py             # Admin-only routes
│   │   ├── employee.py          # Employee CRUD routes
│   │   └── profile.py           # Employee self-service profile routes
│   │
│   ├── forms/                   # WTForms definitions
│   │   ├── __init__.py
│   │   ├── auth_forms.py
│   │   ├── employee_forms.py
│   │   ├── department_forms.py
│   │   └── user_forms.py
│   │
│   ├── utils/                   # Reusable helpers and security utilities
│   │   ├── __init__.py
│   │   ├── decorators.py        # Role-based access decorators
│   │   ├── validators.py        # Validation helpers
│   │   ├── security.py          # Security headers and session helpers
│   │   └── logging_config.py    # Logging configuration
│   │
│   ├── templates/               # Jinja2 templates
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── auth/
│   │   ├── admin/
│   │   ├── employee/
│   │   └── errors/
│   │
│   └── static/                  # Static frontend assets
│       ├── css/
│       └── js/
│
├── migrations/                  # Database migration files
├── tests/                       # Automated test suite
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_authorization.py
│   ├── test_employee_crud.py
│   ├── test_department_crud.py
│   └── test_security.py
├── instance/                    # Local instance files / SQLite DB
├── seed.py                      # Seed script for demo data
├── run.py                       # Application entry point
├── requirements.txt             # Python dependencies
├── .env.example                 # Example environment configuration
├── .gitignore                   # Git ignore rules
└── README.md                    # Project documentation
```

---

## Setup and Installation Instructions

### Prerequisites

Before running the project locally, ensure the following are installed:

* Python 3.10 or later
* pip
* Git

### 1. Clone the Repository

Replace the placeholder URL with your public GitHub repository link:

```bash
git clone https://github.com/YOUR_USERNAME/employee-management-system.git
cd employee-management-system
```

### 2. Create and Activate a Virtual Environment

**Windows (PowerShell):**

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**

```cmd
python -m venv venv
venv\Scripts\activate
```

**Linux / macOS:**

```bash
python -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file based on `.env.example`.

**Windows (PowerShell):**

```powershell
Copy-Item .env.example .env
```

**Linux / macOS:**

```bash
cp .env.example .env
```

Example values:

```env
FLASK_CONFIG=development
SECRET_KEY=replace-with-a-secure-random-string
DATABASE_URL=sqlite:///instance/app.db
TEST_DATABASE_URL=sqlite:///:memory:
LOG_LEVEL=INFO
```

### 5. Run Database Migrations

If the `migrations/` folder is already included in the repository:

```bash
flask --app run.py db upgrade
```

If migrations need to be initialized for the first time:

```bash
flask --app run.py db init
flask --app run.py db migrate -m "Initial migration"
flask --app run.py db upgrade
```

### 6. Seed the Database

```bash
python seed.py
```

### 7. Run the Application

```bash
python run.py
```

The application should be available at:

```text
http://127.0.0.1:5000
```

---

## Default Demo Credentials

After running `seed.py`, the following demo accounts are available:

| Role     | Username  | Password     |
| -------- | --------- | ------------ |
| Admin    | admin     | Admin1234    |
| Employee | employee1 | Employee1234 |
| Employee | employee2 | Employee1234 |

> These credentials are for local demonstration only and must not be used in a real deployment.

---

## Usage Guidelines

### Admin Workflow

1. Log in using the admin account.
2. Access the **Admin Dashboard**.
3. Manage employee records from the **Employees** section.
4. Create, edit, and delete departments from the **Departments** section.
5. Create user accounts and manage account status from the **Users** section.
6. Review security and activity events from the **Audit Logs** section.

### Employee Workflow

1. Log in using an employee account.
2. Access the **Employee Dashboard**.
3. Open **My Profile** to view assigned employment details.
4. Use **Edit Profile** to update permitted personal details such as phone number and address.

### Important Notes

* Employee users are intentionally restricted from administrative functionality.
* Sensitive actions such as employee and department management are reserved for administrators.
* All key actions are auditable through the logging mechanism.

---

## Security Improvements

This project focuses strongly on secure web application practices. The most important security enhancements implemented are summarized below.

### 1. Secure Authentication

* Passwords are never stored in plain text.
* Authentication is enforced before allowing access to protected routes.

### 2. Role-Based Authorization

* Admin-only views are protected using role-based decorators.
* Employees are restricted to their own limited self-service functionality.

### 3. CSRF Protection

* Forms that modify state include CSRF tokens through Flask-WTF.

### 4. Input Validation

* Both form-level and service-layer validation are used to reject malformed or unsafe input.

### 5. ORM-Based Data Access

* SQLAlchemy is used for database access, reducing the risk of SQL injection caused by unsafe string-built queries.

### 6. Secure Session and Cookie Settings

* Session-related configuration helps reduce browser-side session risks.

### 7. Security Headers

* Response headers are applied to reduce clickjacking, MIME-type confusion, and related browser-based risks.

### 8. Audit Logging

* Security-relevant and administrative actions are recorded for traceability and accountability.

### 9. Custom Error Handling

* Controlled error responses reduce the exposure of internal implementation details.

---

## Testing Process

Testing was used to verify both the **functional correctness** and the **security behaviour** of the system.

### Tools Used

* **Pytest** for automated functional and security-oriented tests
* **pytest-cov** for coverage reporting
* **Bandit** for static analysis of Python code
* **pip-audit** for dependency-level security review

### Test Coverage Areas

The automated test suite covers:

* successful and unsuccessful login
* logout behaviour
* inactive account blocking
* role-based access restrictions
* employee CRUD operations
* department CRUD operations
* employee self-service profile restrictions
* security headers
* password hashing
* SQL injection-style login rejection
* audit logging behaviour

### Current Test Result

The project test suite completed successfully with:

* **22 automated tests passed**

### Run the Test Suite

```bash
pytest -v
```

### Run with Coverage

```bash
pytest --cov=app --cov-report=term-missing
```

### Run Static Security Checks

```bash
bandit -r app
pip-audit
```

---

## Example Security Test Outcomes

The test suite was used to verify several important security properties:

* An employee user cannot access administrator-only routes.
* Invalid login attempts are rejected and logged.
* SQL injection-style input submitted through the login form does not bypass authentication.
* Passwords are stored as hashes rather than plain-text values.
* Restricted employee self-service updates cannot modify unauthorized fields.
* Security headers are returned in HTTP responses.

---

## Repository and Commit History

This repository is intended to show structured development progression rather than a single end-stage code upload. The commit history should reflect meaningful implementation stages such as:

* initial Flask application scaffold
* configuration and extension setup
* model creation
* service-layer implementation
* route and form integration
* template and frontend development
* security control implementation
* automated testing
* documentation and final refinement

This structure helps demonstrate traceable development and clearer project evolution.

---

## Public Repository Link

Replace this placeholder with your actual public repository URL:

```text
https://github.com/Sreedevan1996/Employee-Management-System
```

---

## Contributions

This project was implemented as an individual academic submission. The design, implementation structure, testing workflow, and documentation were prepared for educational assessment purposes.

---

## References

The following types of sources were used to support implementation and security decisions:

* Flask official documentation
* SQLAlchemy official documentation
* Flask-Login documentation
* Flask-WTF documentation
* OWASP secure web development guidance
* pytest documentation
* Bandit documentation

These should also be listed formally in the report using Harvard referencing style.

---

## License

This repository is provided for **educational purposes only**.

It is not intended for production deployment without further hardening, infrastructure review, and operational security controls.

```
```
