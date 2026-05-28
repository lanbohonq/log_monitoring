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

## Architecture

**Core modules (`core/`):**
- `ssh_client.py` — SSH connection with callback-based API (`log_callback`, `status_callback`). Auto-detects root switching: tries `su -` first, falls back to `sudo su -`. Uses `invoke_shell()` for interactive session.
- `env_manager.py` — CRUD operations for environment configs stored in `environments.json`
- `log_viewer.py` — Log level detection via regex (ERROR/FATAL/WARN/INFO/DEBUG)

**GUI modules (`gui/`):**
- `main_window.py` — Three-area layout: top toolbar (env selector + connect), middle full log, bottom filters + filtered log
- `ssh_worker.py` — QThread wrapper around SSHClient, emits Qt signals for log/status/error
- `log_widget.py` — QTextEdit-based log display with ANSI color mapping
- `filter_widget.py` — Checkbox widget for log level filtering
- `env_dialog.py` — QDialog for managing saved environments

**Entry points:**
- `main.py` — CLI version, reads config from `.env`
- `main_gui.py` — GUI version, reads config from `environments.json`

## Configuration

- `.env` — CLI version config (HOST, PORT, USERNAME, PASSWORD, ROOT_USER, ROOT_PASS, LOG_PATH)
- `environments.json` — GUI version config (multiple saved environments)

Note: `.env` uses `LOG_PATH` (not `PATH`) to avoid collision with the system PATH variable.

## Key Design Decisions

- Root switching is auto-detected: `su -` first (needs root password), then `sudo su -` (needs user password). No manual config needed.
- SSHClient uses callbacks instead of print() so both CLI and GUI can use the same core logic.
- GUI uses QThread for non-blocking SSH operations with signal-based communication.
