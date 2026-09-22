"""Run chat.py in a pseudo-terminal, type each prompt as a person would, and save the screen.

This drives the course's chat.py exactly as a person at the keyboard would, so the
saved transcript comes from chat.py itself. The screen text is also written to a log.
Usage: .venv/bin/python scripts/chat_demo.py MODEL TRANSCRIPT LOG PROMPT [PROMPT ...]
"""
import os
import pty
import select
import sys
import time


def main():
    model, transcript, log, *prompts = sys.argv[1:]
    pid, fd = pty.fork()
    if pid == 0:
        os.execv(sys.executable, [sys.executable, "chat.py", "--model", model, "--transcript", transcript])
    screen = b""

    def pump(until=None, timeout=60):
        nonlocal screen
        deadline = time.time() + timeout
        while time.time() < deadline:
            ready, _, _ = select.select([fd], [], [], 0.1)
            if ready:
                try:
                    chunk = os.read(fd, 4096)
                except OSError:
                    return False
                if not chunk:
                    return False
                screen += chunk
                sys.stdout.write(chunk.decode("utf-8", "replace"))
                sys.stdout.flush()
            if until and screen.rstrip().endswith(until):
                return True
        return False

    def type_line(text):
        for character in text:
            os.write(fd, character.encode())
            pump(timeout=0.04)
        time.sleep(0.4)
        os.write(fd, b"\n")

    pump(until=b"You:")
    for prompt in prompts:
        type_line(prompt)
        pump(until=b"You:")
        time.sleep(0.8)
    type_line("/quit")
    pump(timeout=5)
    os.waitpid(pid, 0)
    with open(log, "w", encoding="utf-8") as handle:
        handle.write(screen.decode("utf-8", "replace").replace("\r\n", "\n"))


if __name__ == "__main__":
    main()
