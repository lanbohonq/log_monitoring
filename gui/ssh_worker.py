from PySide6.QtCore import QThread, Signal


class SSHWorker(QThread):
    """QThread wrapper for SSH log tailing."""
    log_received = Signal(str)
    status_changed = Signal(str)
    error_occurred = Signal(str)
    finished = Signal()

    def __init__(self, env: dict):
        super().__init__()
        self.env = env
        self._client = None

    def run(self):
        try:
            from core.ssh_client import SSHClient

            self._client = SSHClient(
                host=self.env["host"],
                port=int(self.env.get("port", 22)),
                username=self.env["username"],
                password=self.env["password"],
                root_pass=self.env.get("root_pass", ""),
                log_callback=lambda line: self.log_received.emit(line),
                status_callback=lambda msg: self.status_changed.emit(msg),
            )
            self._client.connect()
            self._client.switch_to_root()
            for line in self._client.tail_log(self.env["log_path"]):
                self.log_received.emit(line)
        except Exception as e:
            self.error_occurred.emit(str(e))
        finally:
            self.finished.emit()

    def stop(self):
        """Stop the worker."""
        if self._client:
            self._client.stop()
            self._client.close()
