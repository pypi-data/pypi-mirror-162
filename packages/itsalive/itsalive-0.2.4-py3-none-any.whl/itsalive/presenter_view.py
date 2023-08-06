"""
Implement the presenter view machinery.

Presenter view runs on one main thread and one background thread. The main thread sets up the curses interface, and the
background thread connects to the presentation server to receive updates. The threads are set up this way so the curses
thread can shut down when it receives a Ctrl+d keystroke.
"""
import curses
import json
import socket
import sys
import threading
from typing import Any
from typing import Dict
from typing import List


class PresenterView:
    def __init__(self, address: str, port: int):
        self.address = address
        self.port = port

        self.commands: List[str] = []
        # Set this to None so we print the first command, even if it's at 0.
        self.command_index = None
        self.command_offset = 0
        self.paused = False
        self.exiting = False

        # An event to signal that curses is done setting up, as otherwise there is corruption when the socket tries to
        # write to the output before curses is fully set up.
        self.curses_done = threading.Event()

    def process_command(self, command: Dict[str, Any]):
        """Process a command that came in through the socket."""
        if command["command"] == "initial":
            self.commands = command["data"]
        elif command["command"] == "exit":
            self.exiting = True
        elif command["command"] == "cursor":
            self.command_index = command["index"]
            self.command_offset = command["offset"]
            self.draw_screen()
        elif command["command"] == "pause":
            self.paused = True
            self.draw_screen()
        elif command["command"] == "resume":
            self.paused = False
            self.draw_screen()

    def connect(self):
        """Connect to the specified presentation server."""
        self.sock = socket.socket()
        try:
            self.sock.connect((self.address, self.port))
        except Exception as e:
            self.sock.close()
            sys.exit(
                "There was an error connecting to the presentation server. Please double-check the address and\n"
                "port, and check that no firewall rules are blocking the connection.\n\nThe error was:\n"
                + str(e)
            )

    def run_client(self):
        """Run the TCP client loop."""
        # Wait for curses to set up.
        self.curses_done.wait()

        BUF_SIZE = 2**12
        data = b""
        while True:
            d = self.sock.recv(BUF_SIZE)

            if not d:
                break

            data += d

            if b"\n" not in d:
                continue

            for line in data.decode().strip("\n").split("\n"):
                self.process_command(json.loads(line))
            data = b""
        self.sock.close()

    def draw_screen(self):
        """Draw the screen based on the current status."""
        self.screen.clear()
        y, x = self.screen.getmaxyx()
        self.screen.border()

        top_margin = 1
        left_margin = 1

        midheight = y // 2

        first_command_row = max(top_margin, midheight - self.command_index)
        last_command_row = min(
            y - top_margin * 2, midheight + len(self.commands) - self.command_index
        )

        first_command_offset = max(0, self.command_index - midheight + top_margin)

        # Draw the commands themselves.
        for c, i in enumerate(
            range(first_command_row, last_command_row), start=first_command_offset
        ):
            formatted_command = repr(self.commands[c].rstrip("\n"))[1:-1].encode()

            # Draw comments in green.
            if self.commands[c].startswith("##"):
                color = 2
            else:
                color = 0

            # Draw the sidebar |.
            self.screen.addstr(i, left_margin + 1, "|", curses.color_pair(3))

            # Draw the command in its entirety.
            self.screen.addstr(
                i,
                left_margin + 3,
                formatted_command[: max(0, x - left_margin * 2 - 3)],
                curses.color_pair(color),
            )
            # Update the command color according to keypresses for the current command.
            if c == self.command_index:
                # Set the live_color_offset_end for live command coloring.
                #
                # If it's a very long command that exceeds the terminal window width,
                # perform live updates until we get to the viewable command end
                # according to the terminal width.
                #
                # Otherwise color from the command start to self.command_offset.
                if self.command_offset > max(0, x - left_margin * 2 - 3):
                    live_color_offset_end = max(0, x - left_margin * 2 - 3)
                else:
                    live_color_offset_end = self.command_offset
                self.screen.addstr(
                    i,
                    left_margin + 3,
                    formatted_command[:live_color_offset_end],
                    curses.color_pair(4),
                )

        # Draw the current command marker.
        self.screen.addstr(midheight, left_margin, "->", curses.color_pair(1))

        self.screen.refresh()

        if self.paused:
            # Draw the "Paused" window.
            win = curses.newwin(5, 20, y // 2 - 2, x // 2 - 10)
            win.border()
            win.addstr(2, 7, "PAUSED", curses.color_pair(1))
            win.refresh()

    def curses_init(self, stdscr):
        """Initialize curses."""
        # Set up curses.
        self.screen = stdscr
        curses.curs_set(0)
        self.screen.erase()
        self.screen.refresh()

        # Set up colors.
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_RED, -1)
        curses.init_pair(2, curses.COLOR_GREEN, -1)
        curses.init_pair(3, curses.COLOR_BLUE, -1)
        curses.init_pair(4, curses.COLOR_CYAN, -1)

        # Signal to the socket that we are done setting up curses.
        self.curses_done.set()

    def curses_main(self, stdscr):
        """Set up curses and run the main loop."""
        self.curses_init(stdscr)
        while True:
            key = self.screen.getkey()
            if key == "KEY_RESIZE":
                self.draw_screen()
            elif key == "\x04" or self.exiting:
                sys.exit("Bye!")

    def run(self):
        print("Connecting to the presenter server...")
        self.connect()
        threading.Thread(target=self.run_client, daemon=True).start()
        curses.wrapper(self.curses_main)


def run_presenter_view(address: str, port: int):
    PresenterView(address=address, port=port).run()
