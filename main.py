import signal
import sys

import config
from ssh_client import SSHClient
from log_viewer import print_line


def main():
    config.validate()

    client = SSHClient(
        host=config.HOST,
        port=config.PORT,
        username=config.USERNAME,
        password=config.PASSWORD,
        root_pass=config.ROOT_PASS,
    )

    def cleanup(sig=None, frame=None):
        client.close()
        sys.exit(0)

    signal.signal(signal.SIGINT, cleanup)

    try:
        client.connect()
        client.switch_to_root()
        for line in client.tail_log(config.LOG_PATH):
            print_line(line)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        cleanup()


if __name__ == "__main__":
    main()
