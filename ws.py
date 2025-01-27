#!/usr/bin/env python3
import argparse
import subprocess
import sys
import socket


blue = "\033[94m"
reset = "\033[0m"

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def start_web_server(port=80):
    if is_port_in_use(port):
        print(f"There is already a web server running on port {port}.")
        sys.exit(1)

    command = f"sudo python3 -m http.server {port}"
    try:
        subprocess.run(command, shell=True, check=True)
    except KeyboardInterrupt:
        sys.exit(0)
    except subprocess.CalledProcessError as e:
        print(f"Error starting the web server: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Start a web server.")
    parser.add_argument("port", nargs="?", type=int, help="Port number for the web server")

    args = parser.parse_args()

    if args.port is None:
        start_web_server()
    else:
        start_web_server(args.port)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
