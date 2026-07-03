#!/usr/bin/env python3
"""Menu-bar control for the local-dictation daemon.

Thin control plane over the launchd job — launchd stays the single owner of
the daemon process (crash-restart, logging), this just drives launchctl.
◉ = daemon running, ○ = stopped.
"""

import os
import subprocess
from pathlib import Path

import rumps

LABEL = "com.nino.local-dictation"
PLIST = Path.home() / "Library/LaunchAgents" / f"{LABEL}.plist"
LOG = Path.home() / "Library/Logs/local-dictation.log"
DOMAIN = f"gui/{os.getuid()}"


def launchctl(*args):
    return subprocess.run(["launchctl", *args], capture_output=True, text=True)


def daemon_running():
    return subprocess.run(["pgrep", "-f", "dictate.py"], capture_output=True).returncode == 0


def service_loaded():
    return launchctl("print", f"{DOMAIN}/{LABEL}").returncode == 0


class DictationApp(rumps.App):
    def __init__(self):
        super().__init__("○", quit_button="Quit")
        self.toggle_item = rumps.MenuItem("Start", callback=self.toggle)
        self.menu = [self.toggle_item, rumps.MenuItem("Open Log", callback=self.open_log)]
        self.refresh(None)
        rumps.Timer(self.refresh, 3).start()

    def refresh(self, _):
        running = daemon_running()
        self.title = "◉" if running else "○"
        self.toggle_item.title = "Stop" if running else "Start"

    def toggle(self, _):
        if daemon_running():
            launchctl("bootout", f"{DOMAIN}/{LABEL}")
        elif service_loaded():
            launchctl("kickstart", f"{DOMAIN}/{LABEL}")
        else:
            result = launchctl("bootstrap", DOMAIN, str(PLIST))
            if result.returncode != 0:
                rumps.notification("local-dictation", "failed to start",
                                   result.stderr.strip() or f"is {PLIST} installed?")
        self.refresh(None)

    def open_log(self, _):
        subprocess.run(["open", str(LOG)])


if __name__ == "__main__":
    DictationApp().run()
