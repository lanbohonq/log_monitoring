import re
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QLineEdit, QPushButton, QLabel
)
from PySide6.QtCore import Signal, Qt


class SearchBar(QWidget):
    """Search bar with keyword input and prev/next navigation."""

    search_changed = Signal()
    navigate = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._matches = []
        self._current_index = -1
        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.input = QLineEdit()
        self.input.setPlaceholderText("")
        self.input.setClearButtonEnabled(True)
        self.input.setMinimumWidth(200)

        self.btn_prev = QPushButton("▲")
        self.btn_prev.setFixedWidth(30)
        self.btn_prev.setEnabled(False)

        self.btn_next = QPushButton("▼")
        self.btn_next.setFixedWidth(30)
        self.btn_next.setEnabled(False)

        self.match_label = QLabel("")
        self.match_label.setMinimumWidth(60)
        self.match_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(QLabel("搜索:"))
        layout.addWidget(self.input)
        layout.addWidget(self.btn_prev)
        layout.addWidget(self.btn_next)
        layout.addWidget(self.match_label)
        layout.addStretch()

        self.input.returnPressed.connect(self.find_next)
        self.btn_prev.clicked.connect(self.find_prev)
        self.btn_next.clicked.connect(self.find_next)
        self.input.textChanged.connect(self._on_text_changed)

    def _on_text_changed(self):
        self.search_changed.emit()

    def keyword(self) -> str:
        return self.input.text()

    def update_matches(self, text: str):
        """Recompute match positions from the given text."""
        self._matches.clear()
        self._current_index = -1
        keyword = self.input.text()
        if not keyword:
            self.match_label.setText("")
            self.btn_prev.setEnabled(False)
            self.btn_next.setEnabled(False)
            return

        pattern = re.compile(re.escape(keyword), re.IGNORECASE)
        self._matches = [m.start() for m in pattern.finditer(text)]

        if self._matches:
            self._current_index = 0
            self.match_label.setText(f"1/{len(self._matches)}")
            self.btn_prev.setEnabled(True)
            self.btn_next.setEnabled(True)
        else:
            self.match_label.setText("0/0")
            self.btn_prev.setEnabled(False)
            self.btn_next.setEnabled(False)

    def current_position(self) -> int | None:
        """Return the character offset of the current match, or None."""
        if 0 <= self._current_index < len(self._matches):
            return self._matches[self._current_index]
        return None

    def current_keyword(self) -> str:
        return self.input.text()

    def find_next(self):
        if not self._matches:
            return
        self._current_index = (self._current_index + 1) % len(self._matches)
        self.match_label.setText(f"{self._current_index + 1}/{len(self._matches)}")
        self.navigate.emit()

    def find_prev(self):
        if not self._matches:
            return
        self._current_index = (self._current_index - 1) % len(self._matches)
        self.match_label.setText(f"{self._current_index + 1}/{len(self._matches)}")
        self.navigate.emit()
