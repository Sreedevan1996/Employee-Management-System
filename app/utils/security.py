import secrets
from urllib.parse import urljoin, urlparse

from flask import current_app, request


def configure_security(app):
    """
    Apply baseline security-related Flask configuration.
    Call this in create_app().
    """
    app.config.setdefault("SECRET_KEY", secrets.token_hex(32))
    app.config.setdefault("SESSION_COOKIE_HTTPONLY", True)
    app.config.setdefault("SESSION_COOKIE_SAMESITE", "Lax")
    app.config.setdefault("REMEMBER_COOKIE_HTTPONLY", True)
    app.config.setdefault("REMEMBER_COOKIE_SAMESITE", "Lax")
    app.config.setdefault("WTF_CSRF_ENABLED", True)
    app.config.setdefault("WTF_CSRF_TIME_LIMIT", 3600)
    app.config.setdefault("MAX_CONTENT_LENGTH", 2 * 1024 * 1024)  # 2 MB

    # Keep secure cookies enabled in production-like environments
    app.config.setdefault("SESSION_COOKIE_SECURE", not app.debug and not app.testing)
    app.config.setdefault("REMEMBER_COOKIE_SECURE", not app.debug and not app.testing)


def register_security_headers(app):
    """
    Register secure response headers for all outgoing responses.
    Call this in create_app().
    """

    @app.after_request
    def add_security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        response.headers["Cache-Control"] = "no-store"

        # Simple CSP suitable for a server-rendered Flask app with local assets
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data:; "
            "font-src 'self'; "
            "object-src 'none'; "
            "base-uri 'self'; "
            "form-action 'self'; "
            "frame-ancestors 'none'"
        )

        return response


def get_client_ip() -> str | None:
    """
    Safely retrieve the client IP address.
    """
    forwarded_for = request.headers.get("X-Forwarded-For", "").split(",")[0].strip()
    return forwarded_for or request.remote_addr


def is_safe_url(target: str) -> bool:
    """
    Prevent open redirect issues by ensuring the target URL belongs
    to the same host as the current application.
    """
    if not target:
        return False

    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))

    return (
        test_url.scheme in {"http", "https"}
        and ref_url.netloc == test_url.netloc
    )


def apply_login_manager_settings(login_manager):
    """
    Optional helper if you want centralized login-manager settings.
    """
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Please log in to access this page."
    login_manager.login_message_category = "warning"
    login_manager.session_protection = "strong"