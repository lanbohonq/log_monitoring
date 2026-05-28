import re

# ANSI color codes
COLORS = {
    "ERROR": "\033[91m",   # Red
    "FATAL": "\033[91m",   # Red
    "WARN":  "\033[93m",   # Yellow
    "INFO":  "\033[92m",   # Green
    "DEBUG": "\033[90m",   # Gray
}
RESET = "\033[0m"

LEVEL_PATTERN = re.compile(r"\b(ERROR|FATAL|WARN(?:ING)?|INFO|DEBUG)\b", re.IGNORECASE)


def detect_level(line: str) -> str | None:
    """Extract log level from a line, return uppercase level or None."""
    match = LEVEL_PATTERN.search(line)
    if not match:
        return None
    level = match.group(1).upper()
    if level == "WARNING":
        level = "WARN"
    return level


def colorize(line: str) -> str:
    """Apply ANSI color based on detected log level."""
    level = detect_level(line)
    if level and level in COLORS:
        return f"{COLORS[level]}{line}{RESET}"
    return line


def print_line(line: str):
    """Detect level, colorize, and print."""
    print(colorize(line), flush=True)
