import sys
import time
import paramiko


class SSHClient:
    def __init__(self, host: str, port: int, username: str, password: str,
                 root_pass: str = "", log_callback=None, status_callback=None):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.root_pass = root_pass or password
        self.client = None
        self.shell = None
        self.log_callback = log_callback or print
        self.status_callback = status_callback or (lambda msg: None)
        self._running = False

    def connect(self):
        """Establish SSH connection."""
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.status_callback(f"Connecting to {self.host}:{self.port}...")
        self.client.connect(
            hostname=self.host,
            port=self.port,
            username=self.username,
            password=self.password,
            timeout=10,
        )
        self.status_callback("SSH connected.")

    def _read_until(self, shell, keywords: list[str], timeout: int = 10) -> str:
        """Read shell output until one of the keywords appears or timeout."""
        output = ""
        deadline = time.time() + timeout
        while time.time() < deadline:
            if shell.recv_ready():
                chunk = shell.recv(65536).decode("utf-8", errors="replace")
                output += chunk
                lower = output.lower()
                for kw in keywords:
                    if kw in lower:
                        return output
            time.sleep(0.1)
        return output

    def switch_to_root(self):
        """Try su first, fallback to sudo su."""
        self.shell = self.client.invoke_shell()
        time.sleep(1)
        if self.shell.recv_ready():
            self.shell.recv(65536)

        # Strategy 1: su -
        self.status_callback("Trying: su -")
        self.shell.send("su -\n")
        output = self._read_until(self.shell, ["password", "su:"])
        if "su:" in output.lower() and "password" not in output.lower():
            self.status_callback("su not available, trying sudo...")
        else:
            self.shell.send(f"{self.root_pass}\n")
            time.sleep(2)
            output = ""
            if self.shell.recv_ready():
                output = self.shell.recv(65536).decode("utf-8", errors="replace")
            if "#" in output or "root@" in output:
                self.status_callback("Root access via su.")
                return
            self.status_callback("su failed.")

        # Strategy 2: sudo su -
        self.status_callback("Trying: sudo su -")
        self.shell.send("sudo su -\n")
        output = self._read_until(self.shell, ["password"])
        if "password" in output.lower():
            self.shell.send(f"{self.password}\n")
            time.sleep(2)
            output = ""
            if self.shell.recv_ready():
                output = self.shell.recv(65536).decode("utf-8", errors="replace")
            if "#" in output or "root@" in output:
                self.status_callback("Root access via sudo su.")
                return

        raise RuntimeError("Failed to get root access")

    def tail_log(self, path: str):
        """Execute tail -f and yield lines in real-time."""
        self.status_callback(f"Monitoring: {path}")
        self.shell.send(f"tail -f {path}\n")
        self._running = True
        buffer = ""
        while self._running:
            if self.shell.recv_ready():
                chunk = self.shell.recv(65536).decode("utf-8", errors="replace")
                buffer += chunk
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    line = line.rstrip("\r")
                    if line:
                        yield line
            else:
                time.sleep(0.1)

    def stop(self):
        """Stop tailing."""
        self._running = False

    def close(self):
        """Close SSH connection."""
        self._running = False
        if self.shell:
            self.shell.close()
        if self.client:
            self.client.close()
        self.status_callback("Connection closed.")
