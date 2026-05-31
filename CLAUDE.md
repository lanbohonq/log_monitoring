# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Python-based remote log monitoring tool for Linux servers. Connects via SSH, auto-switches to root (tries `su` then `sudo su`), and streams log files in real-time with log-level color highlighting. Available as both CLI and GUI (PySide6) versions.

## Running

```bash
# CLI version
python main.py

# GUI version
python main_gui.py
```

## Dependencies

```bash
pip install -r requirements.txt
```

Requires: paramiko, python-dotenv, pyside6

## Building

PyInstaller spec is at `LogMonitoringTool.spec`. Produces a windowed (no console) exe named `LogMonitoringTool` with the `1f310.ico` icon.

```bash
pyinstaller LogMonitoringTool.spec
```

## Architecture

The codebase has two layers of the same modules:

- **Root-level files** (`config.py`, `ssh_client.py`, `log_viewer.py`) — the original CLI-only versions. `config.py` reads `.env`; `ssh_client.py` uses `print()` directly; `log_viewer.py` provides ANSI terminal colors.
- **`core/` package** — refactored versions with callback-based APIs (`log_callback`, `status_callback`) so both CLI and GUI can share the same SSH logic. The GUI version exclusively uses `core/`.

**Core modules (`core/`):**
- `ssh_client.py` — SSH connection with callback-based API. Auto-detects root switching: tries `su -` first, falls back to `sudo su -`. Uses `invoke_shell()` for interactive session. Has a `stop()` method for graceful shutdown.
- `env_manager.py` — CRUD operations for environment configs stored in `environments.json`

**GUI modules (`gui/`):**
- `main_window.py` — Three-area layout: top toolbar (env selector + connect/disconnect), middle full log, bottom filters + filtered log. Has a menu bar with environment management dialog.
- `ssh_worker.py` — QThread wrapper around `core.ssh_client.SSHClient`, emits Qt signals (`log_received`, `status_changed`, `error_occurred`, `finished`)
- `log_widget.py` — QTextEdit-based log display with Qt color mapping. Caps at 10,000 lines (`MAX_LINES`), auto-trims oldest. Contains its own `detect_level()` function (duplicates the regex from root `log_viewer.py`).
- `filter_widget.py` — Checkbox widget for log level filtering, emits `filter_changed` signal
- `env_dialog.py` — QDialog for managing saved environments

**Entry points:**
- `main.py` — CLI version, reads config from `.env`
- `main_gui.py` — GUI version, reads config from `environments.json`

## Configuration

- `.env` — CLI version config (HOST, PORT, USERNAME, PASSWORD, ROOT_USER, ROOT_PASS, LOG_PATH)
- `environments.json` — GUI version config (multiple saved environments, auto-created by `core/env_manager.py`)

Note: `.env` uses `LOG_PATH` (not `PATH`) to avoid collision with the system PATH variable.

## Key Design Decisions

- Root switching is auto-detected: `su -` first (needs root password), then `sudo su -` (needs user password). No manual config needed.
- `core/ssh_client.py` uses callbacks instead of print() so both CLI and GUI can use the same core logic.
- GUI uses QThread for non-blocking SSH operations with signal-based communication.
- Log level detection regex (`\b(ERROR|FATAL|WARN(?:ING)?|INFO|DEBUG)\b`) is duplicated in `log_viewer.py` and `gui/log_widget.py` — keep them in sync if changed.
