#!/usr/bin/env python3

"""
DPDK telemetry data over REST API
"""

import argparse
import json
import socket
import time
import threading
from collections import defaultdict
from flask import (Flask, jsonify)

app = Flask(__name__)

rate_date = defaultdict(dict)
sock_telemetry = None

@app.route("/ethdev/stats/rate")
def pps():
    return jsonify(rate_date["pps"])

@app.route("/ethdev/stats")
def ethdev_stats():
    sock_telemetry.connect_and_get("/ethdev/stats")
    return jsonify(sock_telemetry.stats["/ethdev/stats"])

@app.route("/ethdev/info")
def ethdev_info():
    sock_telemetry.connect_and_get("/ethdev/info")
    return jsonify(sock_telemetry.stats["/ethdev/info"])

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

class DPDKTelemetry:
    def __init__(self, sock_path, period):
        self.sock_path = sock_path
        self.period = period
        self.sock = None
        self.max_out_len = 0
        self.port_ids = []
        self.stats = defaultdict(dict)

    def connect_socket(self):
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_SEQPACKET)
        self.sock.connect(self.sock_path)
        print(f"Socket successfully connected to {self.sock_path}")
        data = json.loads(self.sock.recv(1024).decode())
        self.max_out_len = data["max_output_len"]
        self.port_ids = self.cmd("/ethdev/list")["/ethdev/list"]
        
    def cmd(self, c):
        self.sock.send(c.encode())
        return json.loads(self.sock.recv(self.max_out_len))
    
    def assemble_url_from_all_ports(self, url):
        assembled_info = {}
        for i in self.port_ids:
            data = self.cmd(f"{url},{i}")
            assembled_info[i] = data[url]
        return assembled_info
            
    def connect_and_get(self, url):
        try:
            self.connect_socket()
            self.stats[url] = self.assemble_url_from_all_ports(url)
        except Exception as e:
            e = f"{self.sock_path}: {e}"
            print(f"error: {e}")
            self.stats = defaultdict(dict)
        finally:
            if self.sock is not None:
                self.sock.close()
                self.sock = None

class ConsoleThread(DPDKTelemetry, threading.Thread):
    def __init__(self, sock_path, period):
        threading.Thread.__init__(self)
        self.shutdown_flag = threading.Event()
        super().__init__(sock_path, period)

    def run(self):
        print('Thread #%s started' % self.ident)
        terminate = False
        connection_retry = False
        while not self.shutdown_flag.is_set(): 
            try:
                rate_date["pps"] = defaultdict(dict)
                if self.sock is not None:
                    self.sock.close()
                    self.sock = None
                if connection_retry:
                    print("Retry socket Connection in 1 second...")
                    time.sleep(1)
                    connection_retry = False
                self.connect_socket()
                cur = self.assemble_url_from_all_ports("/ethdev/stats")
                while not self.shutdown_flag.is_set():
                    time.sleep(self.period)
                    new = self.assemble_url_from_all_ports("/ethdev/stats")
                    print("---")
                    for i,stats in new.items():
                        rx = (stats["ipackets"] - cur[i]["ipackets"]) / self.period
                        drop = (stats["imissed"] - cur[i]["imissed"]) / self.period
                        tx = (stats["opackets"] - cur[i]["opackets"]) / self.period
                        if rx == 0 and tx == 0 and drop == 0:
                            continue
                        rate_date["pps"][i] = {"rx": rx, "drop": drop, "tx": tx}
                        print(
                            f"{i}:",
                            f"RX={human_readable(rx)} pkt/s",
                            f"DROP={human_readable(drop)} pkt/s",
                            f"TX={human_readable(tx)} pkt/s",
                        )
                    cur = new
            except KeyboardInterrupt:
                terminate = True
            except Exception as e:
                e = f"{self.sock_path}: {e}"
                print(f"error: {e}")
                connection_retry = True
            finally:
                if self.sock is not None:
                    self.sock.close()
                    self.sock = None
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
        "-f",
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
        default=0,
        help="""
        Time interval between each statistics sample,
        default to 0 means rate caculation such as pps is disabled.
        """,
    )
    parser.add_argument(
        "-p",
        "--port",
        type=int,
        default=9001,
        help="""
        REST API port for statistics polling.
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

    global sock_telemetry
    sock_telemetry = DPDKTelemetry(sock_path, args.time)
    enable_console_thread = (args.time != 0)
    if enable_console_thread:
        console_thread = ConsoleThread(sock_path, args.time)
        console_thread.start()
    try:
        app.run(host="0.0.0.0", port=args.port, debug=False, use_reloader=False)
    except Exception as e:
        print(f"error: {e}")
    finally:
        if enable_console_thread:
            console_thread.shutdown_flag.set()
    if enable_console_thread:
        console_thread.join()

if __name__ == "__main__":
    main()
