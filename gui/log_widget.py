from PySide6.QtWidgets import QTextEdit
from PySide6.QtGui import QTextCursor, QColor
from PySide6.QtCore import Qt
import re

COLORS = {
    "ERROR": QColor("#FF4444"),
    "FATAL": QColor("#FF4444"),
    "WARN": QColor("#FFAA00"),
    "INFO": QColor("#44FF44"),
    "DEBUG": QColor("#888888"),
}

LEVEL_PATTERN = re.compile(r"\b(ERROR|FATAL|WARN(?:ING)?|INFO|DEBUG)\b", re.IGNORECASE)
MAX_LINES = 10000


def detect_level(line: str) -> str | None:
    """Extract log level from a line."""
    match = LEVEL_PATTERN.search(line)
    if not match:
        return None
    level = match.group(1).upper()
    if level == "WARNING":
        level = "WARN"
    return level


class LogWidget(QTextEdit):
    """Read-only log display with color coding."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setFontFamily("Consolas")
        self._line_count = 0

    def append_log(self, text: str, level: str | None = None, auto_scroll: bool = True):
        """Append a log line with optional color."""
        if level is None:
            level = detect_level(text)

        if auto_scroll:
            cursor = self.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.End)
            self.setTextCursor(cursor)

            if level and level in COLORS:
                self.setTextColor(COLORS[level])
            else:
                self.setTextColor(QColor("#FFFFFF"))

            self.insertPlainText(text + "\n")

            scrollbar = self.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())
        else:
            # Use a temporary cursor to avoid moving the visible cursor
            cursor = QTextCursor(self.document())
            cursor.movePosition(QTextCursor.MoveOperation.End)

            if level and level in COLORS:
                color = COLORS[level]
            else:
                color = QColor("#FFFFFF")
            fmt = cursor.charFormat()
            fmt.setForeground(color)
            cursor.setCharFormat(fmt)

            cursor.insertText(text + "\n")

        self._line_count += 1

        # Trim old lines
        if self._line_count > MAX_LINES:
            self._trim_lines()

    def _trim_lines(self):
        """Remove oldest lines to stay under MAX_LINES."""
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.Start)
        lines_to_remove = self._line_count - MAX_LINES
        for _ in range(lines_to_remove):
            cursor.select(QTextCursor.SelectionType.LineUnderCursor)
            cursor.removeSelectedText()
            cursor.deleteChar()
        self._line_count = MAX_LINES

    def clear(self):
        """Clear all content."""
        super().clear()
        self._line_count = 0
