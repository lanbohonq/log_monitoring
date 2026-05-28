from PySide6.QtWidgets import QWidget, QVBoxLayout, QCheckBox
from PySide6.QtCore import Signal, Qt


class FilterWidget(QWidget):
    """Log level filter checkboxes."""
    filter_changed = Signal(list)

    LEVELS = ["ERROR", "WARN", "INFO", "DEBUG"]

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.checkboxes: dict[str, QCheckBox] = {}
        for level in self.LEVELS:
            cb = QCheckBox(level)
            cb.setChecked(True)
            cb.stateChanged.connect(self._on_changed)
            layout.addWidget(cb)
            self.checkboxes[level] = cb

    def _on_changed(self):
        """Emit filter_changed with checked levels."""
        checked = [level for level, cb in self.checkboxes.items() if cb.isChecked()]
        self.filter_changed.emit(checked)

    def get_checked(self) -> list[str]:
        """Return list of checked levels."""
        return [level for level, cb in self.checkboxes.items() if cb.isChecked()]
