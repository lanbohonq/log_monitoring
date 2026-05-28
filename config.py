import os
from dotenv import load_dotenv

load_dotenv()

HOST = os.getenv("HOST", "")
PORT = int(os.getenv("PORT", "22"))
USERNAME = os.getenv("USERNAME", "")
PASSWORD = os.getenv("PASSWORD", "")
ROOT_USER = os.getenv("ROOT_USER", "")
ROOT_PASS = os.getenv("ROOT_PASS", "")
LOG_PATH = os.getenv("LOG_PATH", "/var/log/syslog")


def validate():
    """Validate required config values."""
    errors = []
    if not HOST:
        errors.append("HOST is required")
    if not USERNAME:
        errors.append("USERNAME is required")
    if not PASSWORD:
        errors.append("PASSWORD is required")
    if not LOG_PATH:
        errors.append("LOG_PATH is required")
    if errors:
        raise ValueError("Config errors:\n" + "\n".join(f"  - {e}" for e in errors))
