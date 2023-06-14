#!/usr/bin/env python3

"""
Display DPDK port statistics using the telemetry socket API.
"""

import argparse
import json
import socket
import time
import threading
from flask import Flask

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

def human_readable(value: float) -> str:
    units = ("K", "M", "G")
    i = 0
    unit = ""
    while value >= 1000 and i < len(units):
        unit = units[i]
        value /= 1000
        i += 1
    if unit == "":
        return str(value)
    if value < 100:
        return f"{value:.1f}{unit}"
    return f"{value:.0f}{unit}"

class ConsoleThread(threading.Thread):
    def __init__(self, sock_path, period):
        threading.Thread.__init__(self)
        self.shutdown_flag = threading.Event()
        self.sock_path = sock_path
        self.period = period
   
    def run(self):
        print('Thread #%s started' % self.ident)
        sock = None
        terminate = False
        connection_retry = False

        while not self.shutdown_flag.is_set(): 
            try:
                if connection_retry:
                    time.sleep(5)
                    connection_retry = False
                sock = socket.socket(socket.AF_UNIX, socket.SOCK_SEQPACKET)
                sock.connect(self.sock_path)
                print(f"Socket successfully connected to {self.sock_path}")
                data = json.loads(sock.recv(1024).decode())
                max_out_len = data["max_output_len"]
        
                def cmd(c):
                    sock.send(c.encode())
                    return json.loads(sock.recv(max_out_len))
        
                port_ids = cmd("/ethdev/list")["/ethdev/list"]
        
                def get_stats():
                    all_stats = {}
                    for i in port_ids:
                        data = cmd(f"/ethdev/stats,{i}")
                        all_stats[i] = data["/ethdev/stats"]
                    return all_stats
        
                cur = get_stats()
        
                while not self.shutdown_flag.is_set():
                    time.sleep(self.period)
                    new = get_stats()
                    print("---")
                    for i,stats in new.items():
                        rx = (stats["ipackets"] - cur[i]["ipackets"]) / self.period
                        drop = (stats["imissed"] - cur[i]["imissed"]) / self.period
                        tx = (stats["opackets"] - cur[i]["opackets"]) / self.period
                        if rx == 0 and tx == 0 and drop == 0:
                            continue
                        print(
                            f"{i}:",
                            f"RX={human_readable(rx)} pkt/s",
                            f"DROP={human_readable(drop)} pkt/s",
                            f"TX={human_readable(tx)} pkt/s",
                        )
                    cur = new
        
            except KeyboardInterrupt:
                terminate = True
            except ConnectionRefusedError:
                print(f"Connection refused. Retrying in 5 seconds...")
                connection_retry = True
            except Exception as e:
                if isinstance(e, FileNotFoundError):
                    e = f"{self.sock_path}: {e}"
                print(f"error: {e}")
            finally:
                if sock is not None:
                    sock.close()
                if terminate:
                    break
        print('Thread #%s stopped' % self.ident)

def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    # Create mutually exclusive group for the options
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-s",
        "--sock-path",
        help="""
        Path to the DPDK telemetry UNIX socket,
        Can't be used with --file-prefix.
        """,
    )
    group.add_argument(
        "-p",
        "--file-prefix",
        help="""
        Socket path: /var/run/dpdk/<file-prefix>/dpdk_telemetry.v2,
        Can't be used with --sock-path.
        """,
    )
    parser.add_argument(
        "-t",
        "--time",
        type=int,
        default=1,
        help="""
        Time interval between each statistics sample.
        """,
    )
    args = parser.parse_args()

    if args.sock_path:
        sock_path = args.sock_path
    elif args.file_prefix:
        sock_path = "/var/run/dpdk/" + args.file_prefix + "/dpdk_telemetry.v2"
    else:
        print("Please specify --file-prefix or --sock-path")
        raise SystemExit

    console_thread = ConsoleThread(sock_path, args.time)
    console_thread.start()
    app.run(host="0.0.0.0", port=8000, debug=False, use_reloader=False)
    console_thread.shutdown_flag.set()

if __name__ == "__main__":
    main()
