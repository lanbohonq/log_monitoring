import sys
import time
import paramiko


class SSHClient:
    def __init__(self, host: str, port: int, username: str, password: str,
                 root_pass: str = ""):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.root_pass = root_pass or password  # fallback to user password
        self.client = None
        self.shell = None

    def connect(self):
        """Establish SSH connection."""
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        print(f"Connecting to {self.host}:{self.port} as {self.username}...")
        self.client.connect(
            hostname=self.host,
            port=self.port,
            username=self.username,
            password=self.password,
            timeout=10,
        )
        print("SSH connected.")

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
        # Clear initial banner
        if self.shell.recv_ready():
            self.shell.recv(65536)

        # Strategy 1: su -
        print("Trying: su -")
        self.shell.send("su -\n")
        output = self._read_until(self.shell, ["password", "su:"])
        if "su:" in output.lower() and "password" not in output.lower():
            print("su not available, trying sudo...")
        else:
            self.shell.send(f"{self.root_pass}\n")
            time.sleep(2)
            output = ""
            if self.shell.recv_ready():
                output = self.shell.recv(65536).decode("utf-8", errors="replace")
            if "#" in output or "root@" in output:
                print("Root access via su.")
                return
            print("su failed.")

        # Strategy 2: sudo su -
        print("Trying: sudo su -")
        self.shell.send("sudo su -\n")
        output = self._read_until(self.shell, ["password"])
        if "password" in output.lower():
            self.shell.send(f"{self.password}\n")
            time.sleep(2)
            output = ""
            if self.shell.recv_ready():
                output = self.shell.recv(65536).decode("utf-8", errors="replace")
            if "#" in output or "root@" in output:
                print("Root access via sudo su.")
                return

        print("ERROR: Failed to get root access.", file=sys.stderr)
        sys.exit(1)

    def tail_log(self, path: str):
        """Execute tail -f and yield lines in real-time."""
        print(f"Monitoring: {path}")
        print("-" * 60)
        self.shell.send(f"tail -f {path}\n")
        buffer = ""
        while True:
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

    def close(self):
        """Close SSH connection."""
        if self.shell:
            self.shell.close()
        if self.client:
            self.client.close()
        print("\nConnection closed.")
