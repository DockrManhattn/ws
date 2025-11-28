#!/usr/bin/env python3
"""
Script Name: ws.py
Description: Python script template using ~/.config/ws/config.json for configuration.
Author: dockrmanhattn@gmail.com
Date: 2025-11-28
"""

# =========================
# Import Statements
# =========================
import os
import sys
import json
import logging
import argparse
import re
import socket
import subprocess
import termios
from datetime import datetime
from logging.handlers import RotatingFileHandler

# =========================
# Change these for each new script
# =========================


# =========================
# static variables
# =========================
APPLICATION_NAME = os.path.splitext(os.path.basename(sys.argv[0]))[0]  # Derived from filename
CONFIG_FILENAME = "config.json"      # Config file name
LOG_LEVEL_DEFAULT = "INFO"           # Default console log level

# =========================
# Default Config
# =========================
DEFAULT_CONFIG = {
    "LOG_LEVEL": LOG_LEVEL_DEFAULT,
    "MAX_BYTES": 500_000,            # Approx size for ~1000 lines
    "BACKUP_COUNT": 5,               # Number of rotated logs to keep
    "CURRENT_DIR": os.getcwd()
}

LOG_STYLE = {
    "BLUE": "\u001b[94m",
    "YELLOW": "\u001b[93m",
    "RED": "\u001b[91m",
    "RESET": "\u001b[0m",
    "DEBUG_EMOJI": "{🔧🐛[+]🐛🔧}",
    "INFO_EMOJI": "{🌀🌵[+]🌵🌀}",
    "WARNING_EMOJI": "{⚡⚡[+]⚡⚡}",
    "ERROR_EMOJI": "{🔥💀[+]💀🔥}",
    "CRITICAL_EMOJI": "{🚨🔥[+]🔥🚨}",
    "DEBUG_PREFIX": "{BLUE}{DEBUG_EMOJI}{RESET}",
    "INFO_PREFIX": "{YELLOW}{INFO_EMOJI}{RESET}",
    "WARNING_PREFIX": "{YELLOW}{WARNING_EMOJI}{RESET}",
    "ERROR_PREFIX": "{RED}{ERROR_EMOJI}{RESET}",
    "CRITICAL_PREFIX": "{RED}{CRITICAL_EMOJI}{RESET}",
}

# =========================
# Config Path
# =========================
CONFIG_DIR = os.path.expanduser(f"~/.config/{APPLICATION_NAME}")
CONFIG_PATH = os.path.join(CONFIG_DIR, CONFIG_FILENAME)

# =========================
# Apply logging colors/placeholders
# =========================
def apply_color_prefixes(style):
    replacements = {
        "{BLUE}": style["BLUE"],
        "{YELLOW}": style["YELLOW"],
        "{RED}": style["RED"],
        "{RESET}": style["RESET"],
        "{DEBUG_EMOJI}": style["DEBUG_EMOJI"],
        "{INFO_EMOJI}": style["INFO_EMOJI"],
        "{WARNING_EMOJI}": style["WARNING_EMOJI"],
        "{ERROR_EMOJI}": style["ERROR_EMOJI"],
        "{CRITICAL_EMOJI}": style["CRITICAL_EMOJI"],
    }

    def resolve(template: str) -> str:
        for token, value in replacements.items():
            template = template.replace(token, value)
        return template

    style["DEBUG_PREFIX"] = resolve(style["DEBUG_PREFIX"])
    style["INFO_PREFIX"] = resolve(style["INFO_PREFIX"])
    style["WARNING_PREFIX"] = resolve(style["WARNING_PREFIX"])
    style["ERROR_PREFIX"] = resolve(style["ERROR_PREFIX"])
    style["CRITICAL_PREFIX"] = resolve(style["CRITICAL_PREFIX"])

# =========================
# Helper: Ensure Config Directory and Write Config
# =========================
def write_config(config_data):
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config_data, f, indent=4)
    return CONFIG_PATH

# =========================
# Load Configuration
# =========================
def load_config():
    """Load user config, merging with defaults."""
    config = DEFAULT_CONFIG.copy()
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            try:
                file_cfg = json.load(f)
                if isinstance(file_cfg, dict):
                    config.update(file_cfg)
            except json.JSONDecodeError:
                pass
    return config

# =========================
# Custom Logging Formatter (Console)
# =========================
class CustomFormatter(logging.Formatter):
    def __init__(self, style):
        super().__init__()
        self.style = style

    def format(self, record):
        if record.levelno == logging.DEBUG:
            prefix = self.style["DEBUG_PREFIX"]
        elif record.levelno == logging.INFO:
            prefix = self.style["INFO_PREFIX"]
        elif record.levelno == logging.WARNING:
            prefix = self.style["WARNING_PREFIX"]
        elif record.levelno == logging.ERROR:
            prefix = self.style["ERROR_PREFIX"]
        elif record.levelno == logging.CRITICAL:
            prefix = self.style["CRITICAL_PREFIX"]
        else:
            prefix = ""
        return f"{prefix} {record.getMessage()}"

# =========================
# Plain Formatter for File Logs
# =========================
class PlainFormatter(logging.Formatter):
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')

    def format(self, record):
        message = self.ansi_escape.sub('', record.getMessage())
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return f"[{timestamp}] {record.levelname}: {message}"

# =========================
# Setup Logging with Rotation
# =========================
def setup_logging(config, style, cli_log_level=None):
    console_level_str = cli_log_level or config.get("LOG_LEVEL", LOG_LEVEL_DEFAULT)
    console_level = getattr(logging, console_level_str.upper(), logging.INFO)

    logger = logging.getLogger()

    if logger.handlers:
        for h in list(logger.handlers):
            logger.removeHandler(h)

    logger.setLevel(logging.DEBUG)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(console_level)
    console_handler.setFormatter(CustomFormatter(style))
    logger.addHandler(console_handler)

    # Rotating file handler using config values
    log_file_path = os.path.join(CONFIG_DIR, f"{APPLICATION_NAME}.log")
    file_handler = RotatingFileHandler(
        log_file_path,
        mode="a",
        maxBytes=int(config.get("MAX_BYTES", 500_000)),
        backupCount=int(config.get("BACKUP_COUNT", 5)),
        encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(PlainFormatter())
    logger.addHandler(file_handler)

    return logger, log_file_path

# =========================
# Tail Log Function
# =========================
def tail_log(log_file_path, lines=200):
    if not os.path.exists(log_file_path):
        print(f"Log file not found: {log_file_path}")
        return
    with open(log_file_path, "r", encoding="utf-8") as f:
        all_lines = f.readlines()
        for line in all_lines[-lines:]:
            print(line.rstrip())

# =========================
# Handle Log Option
# =========================
def handle_log_option(args, log_file_path):
    if args.log:
        tail_log(log_file_path, lines=200)
        sys.exit(0)


def suppress_ctrl_c_echo():
    """
    Temporarily disable echoing of control characters (like ^C) on the TTY.
    Returns original settings for restoration.
    """
    if not sys.stdin.isatty():
        return None
    try:
        fd = sys.stdin.fileno()
        attrs = termios.tcgetattr(fd)
        new_attrs = attrs[:]
        new_attrs[3] &= ~termios.ECHOCTL  # lflag: disable echo of control chars
        termios.tcsetattr(fd, termios.TCSANOW, new_attrs)
        return fd, attrs
    except Exception:
        return None


def restore_terminal(settings):
    if not settings:
        return
    fd, attrs = settings
    try:
        termios.tcsetattr(fd, termios.TCSANOW, attrs)
    except Exception:
        pass

# =========================
# Parse CLI Arguments
# =========================
def parse_args():
    parser = argparse.ArgumentParser(description="Template script with configurable logging.")
    parser.add_argument(
        "-log-level",
        type=str.upper,
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Set the console logging level (file logging is always DEBUG)."
    )
    parser.add_argument(
        "-log",
        action="store_true",
        help="Show the last 200 lines of the log file and exit."
    )
    parser.add_argument(
        "port",
        nargs="?",
        type=int,
        default=80,
        help="Port number for the web server (default: 80)."
    )
    return parser.parse_args()


def is_port_in_use(port):
    """
    Check if a TCP port is already bound on localhost.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        return sock.connect_ex(("localhost", port)) == 0


def start_web_server(logger, port=80):
    """
    Start a simple HTTP server on the given port if it is free.
    """
    if is_port_in_use(port):
        logger.error("There is already a web server running on port %s.", port)
        sys.exit(1)

    command = ["sudo", "python3", "-m", "http.server", str(port)]
    server_root = os.getcwd()
    logger.debug("Launching web server from %s on port %s", server_root, port)
    logger.info("Starting web server on port %s...", port)
    term_settings = suppress_ctrl_c_echo()
    try:
        # Run server in its own process group so Ctrl+C hits only this script.
        with subprocess.Popen(command, preexec_fn=os.setsid) as proc:
            try:
                proc.wait()
            except KeyboardInterrupt:
                # Quietly stop the web server without surfacing child stderr messages.
                proc.terminate()
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    proc.kill()
                logger.debug("Web server on port %s stopped.", port)
                sys.exit(0)

            if proc.returncode not in (0, None):
                logger.error("Web server exited with code %s", proc.returncode)
                sys.exit(proc.returncode)
            logger.debug("Web server on port %s stopped (return code %s).", port, proc.returncode)
    except subprocess.CalledProcessError as exc:
        logger.error("Error starting the web server: %s", exc)
        sys.exit(1)
    finally:
        restore_terminal(term_settings)


# =========================
# Main Function
# =========================

def main():
    args = parse_args()
    config = load_config()
    style = LOG_STYLE.copy()
    apply_color_prefixes(style)

    # Create the config file
    write_config(config)
    
    # Setup Logging
    logger, log_file_path = setup_logging(config, style, cli_log_level=args.log_level)
    
    # Show log messages for debugging if -log arg is passed.
    handle_log_option(args, log_file_path)

    # Args have been parsed, logging has been established
    start_web_server(logger, args.port)

if __name__ == "__main__":
    main()
