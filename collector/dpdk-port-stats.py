#!/usr/bin/env python3

"""
Display DPDK port statistics using the telemetry socket API.
"""

import argparse
import json
import socket
import time
import signal


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


def wait_for_socket_connection(sock_path):
    connected = False
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_SEQPACKET)
    while not connected:
        try:
            sock.connect(sock_path)
            print(f"Socket successfully connected to {sock_path}")
            connected = True

        except ConnectionRefusedError:
            print(f"Connection refused. Retrying in 5 seconds...")
            time.sleep(5)

        except Exception as e:
            if isinstance(e, FileNotFoundError):
                e = f"{sock_path}: {e}"
            print(f"error: {e}")
            break
    return sock

def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "-s",
        "--sock-path",
        default="/var/run/dpdk/rte/dpdk_telemetry.v2",
        help="""
        Path to the DPDK telemetry UNIX socket.
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

    sock = None
    terminate = False
    connection_retry = False

    signal.signal(signal.SIGTERM, signal.getsignal(signal.SIGINT))
    while True: 
        try:
            if connection_retry:
                time.sleep(5)
                connection_retry = False
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_SEQPACKET)
            sock.connect(args.sock_path)
            print(f"Socket successfully connected to {args.sock_path}")
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
    
            while True:
                time.sleep(args.time)
                new = get_stats()
                print("---")
                for i,stats in new.items():
                    rx = (stats["ipackets"] - cur[i]["ipackets"]) / args.time
                    drop = (stats["imissed"] - cur[i]["imissed"]) / args.time
                    tx = (stats["opackets"] - cur[i]["opackets"]) / args.time
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
                e = f"{args.sock_path}: {e}"
            print(f"error: {e}")
        finally:
            if sock is not None:
                sock.close()
            if terminate:
                break


if __name__ == "__main__":
    main()
