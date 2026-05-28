import json
import os

ENV_FILE = "environments.json"


def _ensure_file():
    """Create environments.json if it doesn't exist."""
    if not os.path.exists(ENV_FILE):
        with open(ENV_FILE, "w", encoding="utf-8") as f:
            json.dump({"environments": []}, f, ensure_ascii=False, indent=2)


def load() -> list[dict]:
    """Load all environments from JSON."""
    _ensure_file()
    with open(ENV_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("environments", [])


def save(environments: list[dict]):
    """Save environments to JSON."""
    with open(ENV_FILE, "w", encoding="utf-8") as f:
        json.dump({"environments": environments}, f, ensure_ascii=False, indent=2)


def add(env: dict):
    """Add a new environment."""
    envs = load()
    envs.append(env)
    save(envs)


def update(index: int, env: dict):
    """Update environment at index."""
    envs = load()
    if 0 <= index < len(envs):
        envs[index] = env
        save(envs)


def delete(index: int):
    """Delete environment at index."""
    envs = load()
    if 0 <= index < len(envs):
        envs.pop(index)
        save(envs)
