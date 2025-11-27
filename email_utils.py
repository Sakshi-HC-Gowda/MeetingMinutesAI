import os
import smtplib
from email.message import EmailMessage
from typing import List, Optional

try:
    import streamlit as st
    HAVE_STREAMLIT = True
except ImportError:
    HAVE_STREAMLIT = False


class EmailConfigError(Exception):
    """Raised when SMTP configuration is missing or invalid."""


def _get_env(name: str, fallback: Optional[str] = None) -> Optional[str]:
    value = os.getenv(name)
    if value is not None:
        return value
    return fallback


def _get_secret(key: str, fallback: Optional[str] = None) -> Optional[str]:
    """Try to get value from Streamlit secrets, fallback to None."""
    if not HAVE_STREAMLIT:
        return fallback
    try:
        return st.secrets.get(key, fallback)
    except Exception:
        return fallback


def load_smtp_settings() -> dict:
    """
    Load SMTP configuration from Streamlit secrets (preferred) or environment variables.
    
    Streamlit secrets (in .streamlit/secrets.toml):
      - email (or smtp_user)
      - password (or smtp_pass)
      - smtp_host
      - smtp_port (default 587)
      - smtp_sender (defaults to email)
      - smtp_use_tls (default true)
    
    Environment variables (fallback):
      - SMTP_HOST (required)
      - SMTP_PORT (default 587)
      - SMTP_USER (required for authenticated servers)
      - SMTP_PASS (required for authenticated servers)
      - SMTP_SENDER or EMAIL_FROM (fallback)
      - SMTP_USE_TLS (default True)
    """
    # Try Streamlit secrets first, then env vars
    host = _get_secret("smtp_host") or _get_env("SMTP_HOST")
    port_str = _get_secret("smtp_port") or _get_env("SMTP_PORT", "587")
    port = int(port_str) if port_str else 587
    
    user = _get_secret("email") or _get_secret("smtp_user") or _get_env("SMTP_USER")
    password = _get_secret("password") or _get_secret("smtp_pass") or _get_env("SMTP_PASS")
    sender = _get_secret("smtp_sender") or _get_env("SMTP_SENDER") or _get_env("EMAIL_FROM") or user
    
    use_tls_str = _get_secret("smtp_use_tls") or _get_env("SMTP_USE_TLS", "true")
    use_tls = (use_tls_str.lower() != "false") if use_tls_str else True

    if not host or not sender:
        raise EmailConfigError("SMTP_HOST and SMTP_SENDER (or email) must be set in secrets.toml or environment variables.")
    if user and not password:
        raise EmailConfigError("Password must be set when email/user is provided.")

    return {
        "host": host,
        "port": port,
        "user": user,
        "password": password,
        "sender": sender,
        "use_tls": use_tls,
    }


def send_summary_email(subject: str, body: str, recipients: List[str]) -> None:
    """
    Send the meeting summary via SMTP.
    Raises EmailConfigError for misconfiguration and smtplib.SMTPException for runtime errors.
    """
    if not recipients:
        raise ValueError("At least one recipient email is required.")

    settings = load_smtp_settings()
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = settings["sender"]
    msg["To"] = ", ".join(recipients)
    msg.set_content(body or "")

    with smtplib.SMTP(settings["host"], settings["port"]) as server:
        if settings["use_tls"]:
            server.starttls()
        if settings["user"]:
            server.login(settings["user"], settings["password"])
        server.send_message(msg)

