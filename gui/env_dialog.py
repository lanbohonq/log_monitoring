from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLineEdit, QFormLayout, QDialogButtonBox, QMessageBox,
    QHeaderView, QSpinBox
)
from PySide6.QtCore import QThread, Signal
from core import env_manager


class EnvDialog(QDialog):
    """Environment management dialog."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("环境配置")
        self.setMinimumSize(700, 400)
        self._setup_ui()
        self._load_envs()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["名称", "主机", "用户"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.table)

        # Buttons
        btn_layout = QHBoxLayout()
        self.btn_add = QPushButton("添加")
        self.btn_edit = QPushButton("编辑")
        self.btn_delete = QPushButton("删除")
        self.btn_add.clicked.connect(self._add)
        self.btn_edit.clicked.connect(self._edit)
        self.btn_delete.clicked.connect(self._delete)
        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_edit)
        btn_layout.addWidget(self.btn_delete)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

    def _load_envs(self):
        """Load environments into table."""
        self.envs = env_manager.load()
        self.table.setRowCount(len(self.envs))
        for i, env in enumerate(self.envs):
            self.table.setItem(i, 0, QTableWidgetItem(env.get("name", "")))
            self.table.setItem(i, 1, QTableWidgetItem(env.get("host", "")))
            self.table.setItem(i, 2, QTableWidgetItem(env.get("username", "")))

    def _add(self):
        """Add new environment."""
        dialog = EnvEditDialog(parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            env = dialog.get_data()
            env_manager.add(env)
            self._load_envs()

    def _edit(self):
        """Edit selected environment."""
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "提示", "请先选择一个环境")
            return
        dialog = EnvEditDialog(self.envs[row], parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            env = dialog.get_data()
            env_manager.update(row, env)
            self._load_envs()

    def _delete(self):
        """Delete selected environment."""
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "提示", "请先选择一个环境")
            return
        reply = QMessageBox.question(
            self, "确认", "确定删除该环境？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            env_manager.delete(row)
            self._load_envs()


class TestConnectionWorker(QThread):
    """Worker thread for testing SSH connection."""
    success = Signal(str)
    error = Signal(str)

    def __init__(self, env_data: dict):
        super().__init__()
        self.env_data = env_data

    def run(self):
        try:
            from core.ssh_client import SSHClient
            client = SSHClient(
                host=self.env_data["host"],
                port=int(self.env_data.get("port", 22)),
                username=self.env_data["username"],
                password=self.env_data["password"],
                root_pass=self.env_data.get("root_pass", ""),
            )
            client.connect()
            client.switch_to_root()
            client.close()
            self.success.emit("连接成功，已获取 root 权限")
        except Exception as e:
            self.error.emit(str(e))


class EnvEditDialog(QDialog):
    """Environment add/edit dialog."""

    def __init__(self, env: dict = None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("编辑环境" if env else "添加环境")
        self.setMinimumWidth(400)
        self._env = env or {}
        self._worker = None
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.name_edit = QLineEdit(self._env.get("name", ""))
        self.host_edit = QLineEdit(self._env.get("host", ""))
        self.port_spin = QSpinBox()
        self.port_spin.setRange(1, 65535)
        self.port_spin.setValue(int(self._env.get("port", 22)))
        self.username_edit = QLineEdit(self._env.get("username", ""))
        self.password_edit = QLineEdit(self._env.get("password", ""))
        self.root_user_edit = QLineEdit(self._env.get("root_user", ""))
        self.root_pass_edit = QLineEdit(self._env.get("root_pass", ""))
        self.log_path_edit = QLineEdit(self._env.get("log_path", "/var/log/syslog"))

        form.addRow("名称:", self.name_edit)
        form.addRow("主机:", self.host_edit)
        form.addRow("端口:", self.port_spin)
        form.addRow("用户名:", self.username_edit)
        form.addRow("密码:", self.password_edit)
        form.addRow("Root用户:", self.root_user_edit)
        form.addRow("Root密码:", self.root_pass_edit)
        form.addRow("日志路径:", self.log_path_edit)

        layout.addLayout(form)

        # Bottom buttons: test on left, ok/cancel on right
        btn_layout = QHBoxLayout()
        self.btn_test = QPushButton("测试连接")
        self.btn_test.clicked.connect(self._test_connection)
        btn_layout.addWidget(self.btn_test)
        btn_layout.addStretch()

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        btn_layout.addWidget(buttons)
        layout.addLayout(btn_layout)

    def _test_connection(self):
        """Test SSH connection with current form data."""
        host = self.host_edit.text().strip()
        username = self.username_edit.text().strip()
        password = self.password_edit.text().strip()
        if not host or not username or not password:
            QMessageBox.warning(self, "提示", "请填写主机、用户名和密码")
            return

        self.btn_test.setEnabled(False)
        self.btn_test.setText("测试中...")

        env_data = {
            "host": host,
            "port": self.port_spin.value(),
            "username": username,
            "password": password,
            "root_pass": self.root_pass_edit.text().strip(),
        }
        self._worker = TestConnectionWorker(env_data)
        self._worker.success.connect(self._on_test_success)
        self._worker.error.connect(self._on_test_error)
        self._worker.finished.connect(self._on_test_done)
        self._worker.start()

    def _on_test_success(self, msg: str):
        QMessageBox.information(self, "成功", msg)

    def _on_test_error(self, error: str):
        QMessageBox.critical(self, "失败", f"连接失败：{error}")

    def _on_test_done(self):
        self.btn_test.setEnabled(True)
        self.btn_test.setText("测试连接")

    def get_data(self) -> dict:
        """Return environment data from form."""
        return {
            "name": self.name_edit.text(),
            "host": self.host_edit.text(),
            "port": self.port_spin.value(),
            "username": self.username_edit.text(),
            "password": self.password_edit.text(),
            "root_user": self.root_user_edit.text(),
            "root_pass": self.root_pass_edit.text(),
            "log_path": self.log_path_edit.text(),
        }
