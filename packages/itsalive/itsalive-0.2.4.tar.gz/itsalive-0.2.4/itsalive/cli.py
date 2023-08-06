#!/usr/bin/env python3
import argparse
import array
import errno
import fcntl
import importlib.metadata
import json
import os
import pty
import re
import select
import signal
import socket
import struct
import sys
import termios
import threading
import tty
from pathlib import Path
from typing import Dict
from typing import List

from .presenter_view import run_presenter_view

try:
    VERSION = importlib.metadata.metadata("itsalive")["Version"]
except Exception:
    VERSION = "0.0.0"


def strip_ansi(text: bytes) -> bytes:
    """Strip all ANSI sequences from `text`."""
    # Python Ansi Regex originally sourced from - https://stackoverflow.com/questions/14693701/how-can-i-remove-the-ansi-escape-sequences-from-a-string-in-python
    # OSC Regex implementation adapted from - https://unix.stackexchange.com/questions/14684/removing-control-chars-including-console-codes-colours-from-script-output
    ansi_escape = re.compile(
        rb"""
       (?:\x1B\]|\x9d).*(?:\x1B\\|[\a\x9c]) # OSC
       |   # or
       (?: # either 7-bit C1, two bytes, ESC Fe (omitting CSI)
           \x1B
           [@-Z\\-_]
       |   # or a single 8-bit byte Fe (omitting CSI)
           [\x80-\x9A\x9C-\x9F]
       |   # or CSI + control codes
           (?: # 7-bit CSI, ESC [
               \x1B\[
           |   # 8-bit CSI, 9B
               \x9B
           )
           [0-?]*  # Parameter bytes
           [ -/]*  # Intermediate bytes
           [@-~]   # Final byte
       )
    """,
        re.VERBOSE,
    )
    return ansi_escape.sub(b"", text)


def load_file(filename: Path) -> List[str]:
    """Load the commands from a file."""
    with filename.expanduser().open("r") as infile:
        cmd_list = infile.read().rstrip("\n").split("\n")

    return cmd_list


def load_commands(filename: Path) -> List[str]:
    """Load commands from a file, processing them as required."""
    new_list = []
    cmd_list = load_file(filename)
    filename = filename.expanduser()
    for command in cmd_list:
        include = re.match(r"^##@include\s+(?P<filename>.*?)$", command)
        if include:
            include_file_name = Path(
                os.path.join(
                    filename.parent, Path(include.group("filename")).expanduser()
                )
            ).resolve()
            if not include_file_name.exists():
                sys.exit("%s does not exist." % include_file_name)
            new_list.extend(load_file(include_file_name))
        else:
            new_list.append(command)

    return new_list


class PresenterServer(threading.Thread):
    """
    The presenter server.

    This class implements a server to which clients can connect to receive
    information about the current state of the presentation.
    """

    daemon = True

    def __init__(self, commands, address, port):
        threading.Thread.__init__(self)
        self.clients = []
        self.commands = commands

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((address, port))
        self.sock.listen()

        self._command_index = 0
        self._command_offset = 0

    def _send_to_client(self, client, data):
        """Send an update to a single client."""
        try:
            client.send(json.dumps(data).encode() + b"\n")
        except BrokenPipeError:
            pass

    def _send_to_all(self, data):
        """Send an update to all connected clients."""
        for client in self.clients:
            self._send_to_client(client, data)

    def _make_initial_message(self) -> Dict[str, str]:
        return {"command": "initial", "data": self.commands}

    def _make_cursor_update_message(self) -> Dict[str, str]:
        return {
            "command": "cursor",
            "index": self._command_index,
            "offset": self._command_offset,
        }

    def _handle_connections(self):
        """Handle new connections."""
        while True:
            connection, client_address = self.sock.accept()
            self._send_to_client(connection, self._make_initial_message())
            self._send_to_client(connection, self._make_cursor_update_message())
            self.clients.append(connection)

    def update_cursor(self, command_index: int, command_offset: int) -> None:
        # This is unsynchronized because I don't anticipate any race conditions,
        # since this is the only place where these variables get written to.
        self._command_index = command_index
        self._command_offset = command_offset
        self._send_to_all(self._make_cursor_update_message())

    def send_command(self, command: str) -> None:
        self._send_to_all({"command": command})

    def run_server(self):
        """Run the TCP server to accent connections on a different thread."""
        threading.Thread(target=self._handle_connections, daemon=True).start()

    def shutdown(self):
        self.send_command("exit")
        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()


class Raw:
    def __init__(self, fd):
        self.fd = fd
        self.restore = False

    def __enter__(self):
        try:
            self.mode = tty.tcgetattr(self.fd)
            tty.setraw(self.fd)
            self.restore = True
        except tty.error:  # This is the same as termios.error
            pass

    def __exit__(self, type, value, traceback):
        if self.restore:
            tty.tcsetattr(self.fd, tty.TCSAFLUSH, self.mode)


class Player:
    def __init__(
        self,
        command_filename: Path,
        env=os.environ.copy(),
        speed=1,
        address=None,
        port=None,
    ):
        self.master_fd = None
        self.paused = False
        # Which command in the list we're at.
        self.command_index = 0
        # Where in the command we currently are.
        self.command_offset = 0
        self.env = env
        self.speed = max(0, int(speed))

        # Read the commands from the file into a list of one per line.
        commands = load_commands(command_filename)
        # Add a blank command to the end, so we don't exit prematurely.
        self.commands = commands + [""]

        self.ps = PresenterServer(self.commands, address=address, port=port)
        self.ps.run_server()

    @property
    def _current_command(self) -> str:
        return self.commands[self.command_index]

    @property
    def _is_first_command(self) -> bool:
        """Return whether this is the first command."""
        return self.command_index == 0

    @property
    def _is_last_command(self) -> bool:
        """Return whether this is the last command."""
        return self.command_index >= len(self.commands) - 1

    def _reset_command(self):
        """Reset the current command to the beginning and send it."""
        self.command_offset = 0

        self.ps.update_cursor(self.command_index, self.command_offset)

    def _set_paused(self, paused: bool):
        """Pause or resume playback."""
        self.paused = paused
        if self.paused:
            self.ps.send_command("pause")
        else:
            self.ps.send_command("resume")

    def _next_command(self):
        """Change the command index to the next command."""
        while True:
            if self._is_last_command:
                self.ps.shutdown()
                sys.exit()

            self.command_index += 1

            # Initiate a command-file-driven pause. When '##@pause' is encountered
            # automatic playback will be paused. The next command will be ready
            # for use when manually resumed.
            #
            # ##@pause is executed following a command with carriage return. When
            # using the skip command combinations (Ctrl+f / Ctrl+g), this is ignored.
            if self._current_command == ("##@pause") and not self.skip_keypress:
                self._set_paused(True)

            # Skip over comments.
            if not self._current_command.startswith("##"):
                self._reset_command()
                break

    def _previous_command(self):
        """Change the command index to the previous command."""
        while True:
            self.command_index = max(0, self.command_index - 1)

            if not self._current_command.startswith("##"):
                self._reset_command()
                break

    def _set_pty_size(self):
        """Set the window size of the child pty based on the window size of our own controlling terminal."""
        # Get the terminal size of the real terminal, set it on the pseudoterminal.
        if os.isatty(pty.STDOUT_FILENO):
            buf = array.array("h", [0, 0, 0, 0])
            fcntl.ioctl(pty.STDOUT_FILENO, termios.TIOCGWINSZ, buf, True)
        else:
            buf = array.array("h", [24, 80, 0, 0])

        fcntl.ioctl(self.master_fd, termios.TIOCSWINSZ, buf)

    def _write_stdout(self, data):
        """Write to stdout as if the child process had written the data."""
        os.write(pty.STDOUT_FILENO, data)

    def _handle_master_read(self, data):
        """Handle new data on child process stdout."""
        self._write_stdout(data)

    def _write_master(self, data, passthrough=False):
        """Write to the child process from its controlling terminal."""
        command_end = False
        if passthrough:
            while data:
                n = os.write(self.master_fd, data)
                data = data[n:]
            return

        data = strip_ansi(data)
        if not data:
            # Sometimes we get pure ANSI sequences, just ignore those.
            return

        next_char = self._current_command[
            self.command_offset : self.command_offset + self.speed
        ]
        if not next_char:
            if b"\r" not in data and b"\n" not in data:
                return
            else:
                next_char = "\n"
                command_end = True

        os.write(self.master_fd, next_char.encode())
        self.command_offset += self.speed
        if command_end:
            self._next_command()
        else:
            self.ps.update_cursor(self.command_index, self.command_offset)

    def _handle_stdin_read(self, data):
        """Handle new data on child process stdin."""
        # Register for when a skip key (Ctrl+f / Ctrl+g) is used
        self.skip_keypress = False

        if data == b"\x10":  # Ctrl+p
            self._set_paused(True)
            return
        elif data == b"\x12":  # Ctrl+r
            self._set_paused(False)
            return

        # If we aren't paused, accept commands.
        if self.paused:
            self._write_master(data, passthrough=True)
        else:
            if data == b"\x04":  # Ctrl+d
                self.ps.shutdown()
                sys.exit("Abort!")
            elif data == b"\x05":  # Ctrl+e
                # Type the rest of the command by setting the speed to the entire command,
                # then emitting a single character so it types everything up to the newline.
                speed_backup = self.speed
                self.speed = len(self._current_command.encode())
                self._write_master(b"a")
                self.speed = speed_backup
            elif data == b"\x15":  # Ctrl+u
                # Pass it through.
                self._write_master(data, passthrough=True)
                self._reset_command()
            elif data == b"\x06":  # Ctrl+f
                # Go to the next command.
                if not self._is_last_command:
                    self.skip_keypress = True
                    self._next_command()
            elif data == b"\x07":  # Ctrl+g
                # Go to the previous command.
                self.skip_keypress = True
                self._previous_command()
            else:
                self._write_master(data)

    def _signals(self, signal_list):
        old_handlers = []
        for sig, handler in signal_list:
            old_handlers.append((sig, signal.signal(sig, handler)))
        return old_handlers

    def _copy(self, signal_fd):
        """
        Run the main select loop.

        Passes control to _master_read() or _stdin_read() when new data arrives.
        """
        fds = [self.master_fd, pty.STDIN_FILENO, signal_fd]

        while True:
            try:
                rfds, wfds, xfds = select.select(fds, [], [])
            except OSError as e:  # Python >= 3.3
                if e.errno == errno.EINTR:
                    continue
            except select.error as e:  # Python < 3.3
                if e.args[0] == 4:
                    continue

            if self.master_fd in rfds:
                data = os.read(self.master_fd, 1024)
                if not data:  # Reached EOF.
                    fds.remove(self.master_fd)
                else:
                    self._handle_master_read(data)

            if pty.STDIN_FILENO in rfds:
                data = os.read(pty.STDIN_FILENO, 1024)
                if not data:
                    fds.remove(pty.STDIN_FILENO)
                else:
                    self._handle_stdin_read(data)

            if signal_fd in rfds:
                data = os.read(signal_fd, 1024)
                if data:
                    signals = struct.unpack("%uB" % len(data), data)
                    for sig in signals:
                        if sig in [
                            signal.SIGCHLD,
                            signal.SIGHUP,
                            signal.SIGTERM,
                            signal.SIGQUIT,
                        ]:
                            os.close(self.master_fd)
                            return
                        elif sig == signal.SIGWINCH:
                            self._set_pty_size()

    def play(self):
        """Start the player."""
        self._reset_command()

        command = ["sh", "-c", os.environ.get("SHELL") or "sh"]
        pid, self.master_fd = pty.fork()

        if pid == pty.CHILD:
            os.execvpe(command[0], command, self.env)

        pipe_r, pipe_w = os.pipe()
        flags = fcntl.fcntl(pipe_w, fcntl.F_GETFL, 0)
        flags = flags | os.O_NONBLOCK
        flags = fcntl.fcntl(pipe_w, fcntl.F_SETFL, flags)

        signal.set_wakeup_fd(pipe_w)

        old_handlers = self._signals(
            map(
                lambda s: (s, lambda signal, frame: None),
                [
                    signal.SIGWINCH,
                    signal.SIGCHLD,
                    signal.SIGHUP,
                    signal.SIGTERM,
                    signal.SIGQUIT,
                ],
            )
        )

        self._set_pty_size()

        with Raw(pty.STDIN_FILENO):
            try:
                # The main loop function, where all the typing work happens.
                self._copy(pipe_r)
            except (IOError, OSError):
                pass

        self._signals(old_handlers)

        os.waitpid(pid, 0)


def main():
    parser = argparse.ArgumentParser(description="It's a live.")
    parser.add_argument(
        "command_file",
        metavar="command_file",
        type=str,
        help="The command file to read.",
    )
    parser.add_argument(
        "--address",
        dest="address",
        type=str,
        default="127.0.0.1",
        help="The address to listen on/connect to for presenter view (default: %(default)s).",
    )
    parser.add_argument(
        "--port",
        dest="port",
        type=int,
        default=5345,
        help="The port to listen on/connect to for presenter view (default: %(default)s).",
    )
    parser.add_argument(
        "-s",
        "--speed",
        dest="speed",
        type=int,
        default=1,
        help="How many characters to type out when you type one (default: %(default)s).",
    )
    parser.add_argument(
        "-c", "--clear", action="store_true", help="Clear the screen before starting"
    )
    parser.add_argument("--version", action="version", version="%(prog)s " + VERSION)

    args = parser.parse_args()
    if args.clear:
        # From https://stackoverflow.com/a/52949759/28196.
        print("{}[2J{}[;H".format(chr(27), chr(27)))

    if args.command_file == "presenter_view":
        run_presenter_view(args.address, args.port)
    else:
        Player(
            Path(args.command_file),
            speed=args.speed,
            address=args.address,
            port=args.port,
        ).play()


if __name__ == "__main__":
    main()
