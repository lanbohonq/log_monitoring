from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QComboBox, QPushButton, QLabel, QSplitter
)
from PySide6.QtCore import Qt
from gui.log_widget import LogWidget, detect_level
from gui.filter_widget import FilterWidget
from gui.env_dialog import EnvDialog
from gui.ssh_worker import SSHWorker
from core import env_manager


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("日志监控工具")
        self.setMinimumSize(1000, 700)
        self._worker = None
        self._setup_ui()
        self._load_envs()

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)

        # Menu bar
        menubar = self.menuBar()
        env_menu = menubar.addMenu("环境配置")
        env_action = env_menu.addAction("管理环境")
        env_action.triggered.connect(self._open_env_dialog)

        # Toolbar
        toolbar = QHBoxLayout()
        self.env_combo = QComboBox()
        self.env_combo.setMinimumWidth(200)
        self.btn_connect = QPushButton("连接")
        self.btn_disconnect = QPushButton("断开")
        self.btn_disconnect.setEnabled(False)
        self.status_label = QLabel("未连接")
        self.status_label.setStyleSheet("color: gray;")

        self.btn_connect.clicked.connect(self._connect)
        self.btn_disconnect.clicked.connect(self._disconnect)

        toolbar.addWidget(QLabel("环境:"))
        toolbar.addWidget(self.env_combo)
        toolbar.addWidget(self.btn_connect)
        toolbar.addWidget(self.btn_disconnect)
        toolbar.addStretch()
        toolbar.addWidget(self.status_label)
        main_layout.addLayout(toolbar)

        # Log areas with splitter
        splitter = QSplitter(Qt.Orientation.Vertical)

        # Full log (middle)
        self.full_log = LogWidget()
        splitter.addWidget(self.full_log)

        # Bottom area
        bottom = QWidget()
        bottom_layout = QHBoxLayout(bottom)
        bottom_layout.setContentsMargins(0, 0, 0, 0)

        self.filter_widget = FilterWidget()
        self.filter_widget.filter_changed.connect(self._on_filter_changed)
        bottom_layout.addWidget(self.filter_widget)

        self.filtered_log = LogWidget()
        bottom_layout.addWidget(self.filtered_log, 1)

        splitter.addWidget(bottom)
        splitter.setSizes([500, 200])
        main_layout.addWidget(splitter)

    def _load_envs(self):
        """Load environments into combo box."""
        self.env_combo.clear()
        envs = env_manager.load()
        for env in envs:
            self.env_combo.addItem(env.get("name", ""), env)

    def _open_env_dialog(self):
        """Open environment management dialog."""
        dialog = EnvDialog(self)
        dialog.exec()
        self._load_envs()

    def _connect(self):
        """Connect to selected environment."""
        env = self.env_combo.currentData()
        if not env:
            self.status_label.setText("请先选择环境")
            self.status_label.setStyleSheet("color: red;")
            return

        self.btn_connect.setEnabled(False)
        self.btn_disconnect.setEnabled(True)
        self.status_label.setText("连接中...")
        self.status_label.setStyleSheet("color: yellow;")
        self.full_log.clear()
        self.filtered_log.clear()

        self._worker = SSHWorker(env)
        self._worker.log_received.connect(self._on_log_received)
        self._worker.status_changed.connect(self._on_status_changed)
        self._worker.error_occurred.connect(self._on_error)
        self._worker.finished.connect(self._on_finished)
        self._worker.start()

    def _disconnect(self):
        """Disconnect from current environment."""
        if self._worker:
            self._worker.stop()
            self._worker.wait(3000)
            self._worker = None
        self.btn_connect.setEnabled(True)
        self.btn_disconnect.setEnabled(False)
        self.status_label.setText("已断开")
        self.status_label.setStyleSheet("color: gray;")

    def _on_log_received(self, line: str):
        """Handle new log line."""
        level = detect_level(line)
        self.full_log.append_log(line, level)

        # Update filtered view based on checkboxes
        checked = self.filter_widget.get_checked()
        if level and level in checked:
            self.filtered_log.append_log(line, level)
        elif not level:
            self.filtered_log.append_log(line, level)

    def _on_status_changed(self, msg: str):
        """Handle status message."""
        self.status_label.setText(msg)
        self.status_label.setStyleSheet("color: green;" if "connected" in msg.lower() else "color: yellow;")

    def _on_error(self, error: str):
        """Handle error."""
        self.status_label.setText(f"错误: {error}")
        self.status_label.setStyleSheet("color: red;")

    def _on_finished(self):
        """Handle worker finished."""
        self.btn_connect.setEnabled(True)
        self.btn_disconnect.setEnabled(False)

    def _on_filter_changed(self, checked: list[str]):
        """Handle filter change - rebuild filtered log."""
        self.filtered_log.clear()
        # Re-filter from full log content
        full_text = self.full_log.toPlainText()
        for line in full_text.split("\n"):
            if not line.strip():
                continue
            level = detect_level(line)
            if level and level in checked:
                self.filtered_log.append_log(line, level)
            elif not level:
                self.filtered_log.append_log(line, level)

    def closeEvent(self, event):
        """Clean up on window close."""
        self._disconnect()
        event.accept()
