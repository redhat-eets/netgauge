#!/usr/bin/env python3

"""
DPDK telemetry data over REST API
"""

import argparse
import json
import socket
import time
import os
import logging
import signal
from collections import defaultdict
from typing import Iterable
from prometheus_client import start_http_server
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from prometheus_client.core import REGISTRY, CounterMetricFamily
from opentelemetry import metrics
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import SERVICE_NAME, Resource


class DPDKTelemetry:
    def __init__(self, sock_path):
        self.sock_path = sock_path
        self.sock = None
        self.max_out_len = 0
        self.port_ids = []
        self.stats = defaultdict(dict)

    def __del__(self):
        self._close_sock()

    def _close_sock(self):
        if self.sock is not None:
            try:
                self.sock.close()
            except Exception as e:
                e = f"{self.sock_path}: {e}"
                logging.warning(f"Failed to close socket: {e}")
            finally:
                self.sock = None

    def _connect_socket(self):
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_SEQPACKET)
        self.sock.connect(self.sock_path)
        logging.info(f"Socket successfully connected to {self.sock_path}")
        data = json.loads(self.sock.recv(1024).decode())
        self.max_out_len = data["max_output_len"]
        self.port_ids = self._cmd("/ethdev/list")["/ethdev/list"]

    def _cmd(self, c):
        self.sock.send(c.encode())
        return json.loads(self.sock.recv(self.max_out_len))

    def _assemble_from_ports(self, url):
        assembled_info = {}
        for i in self.port_ids:
            data = self._cmd(f"{url},{i}")
            assembled_info[i] = data[url]
        return assembled_info

    def connect_and_get(self, url):
        try:
            if self.sock is None:
                self._connect_socket()
            self.stats[url] = self._assemble_from_ports(url)
        except Exception as e:
            e = f"{self.sock_path}: {e}"
            logging.warning(e)
            self.stats = defaultdict(dict)
            self._close_sock()
        return self.stats[url]

class SocketEventHandler(FileSystemEventHandler):
    def __init__(self, sock_dict):
        self.socks = sock_dict
    def on_created(self, event):
        if event.is_directory:
            app_name = os.path.basename(event.src_path)
            logging.info(f"New DPDK application created: {app_name}")
            self.socks[app_name] = DPDKTelemetry(event.src_path + "/dpdk_telemetry.v2")
    def on_deleted(self, event):
        if event.is_directory:
            app_name = os.path.basename(event.src_path)
            logging.info(f"DPDK application deleted: {app_name}")
            del self.socks[app_name]

class PrometheusCollector(object):
    def __init__(self, sock_dict):
        self.socks = sock_dict

    def collect(self):
        for app, sock in self.socks.items():
            try:
                count = CounterMetricFamily(app, "ethdev stats", labels=[app])
                ethdev_stats = sock.connect_and_get("/ethdev/stats")
                for port, stats in ethdev_stats.items():
                    count.add_metric(['ibytes_' + str(port)], stats["ibytes"])
                    count.add_metric(['ipackets_' + str(port)], stats["ipackets"])
                    count.add_metric(['obytes_' + str(port)], stats["obytes"])
                    count.add_metric(['opackets_' + str(port)], stats["opackets"])
                yield count
            except Exception as e:
                e = f"{app}: {e}"
                logging.warning(e)

class OtlpCollector(object):
    def __init__(self, sock_dict):
        self.socks = sock_dict

    def dpdk_telemetry_callback(self, options: metrics.CallbackOptions) -> Iterable[metrics.Observation]:
        observations = []
        for app, sock in self.socks.items():
            ethdev_stats = sock.connect_and_get("/ethdev/stats")
            for port, stats in ethdev_stats.items():
                observations.append(metrics.Observation(int(stats["ibytes"]), {"app": app, "port": port, "stats": "ibytes"}))
                observations.append(metrics.Observation(int(stats["ipackets"]), {"app": app, "port": port, "stats": "ipackets"}))
                observations.append(metrics.Observation(int(stats["obytes"]), {"app": app, "port": port, "stats": "obytes"}))
                observations.append(metrics.Observation(int(stats["opackets"]), {"app": app, "port": port, "stats": "opackets"}))
        return observations

def initialize_sock_dict(dir, socks):
    for d in os.listdir(dir):
        full_path = os.path.join(dir, d)
        # make sure full_path is a directory
        if os.path.isdir(full_path):
            socks[d] = DPDKTelemetry(full_path + "/dpdk_telemetry.v2")

def main():
    logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)
    logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.WARNING)
    sock_dict = dict()
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "-s",
        "--sock-prefix",
        default="/var/run/dpdk",
        help="""
        Path to the directory which contains the DPDK telemetry sub folders.
        """,
    )
    parser.add_argument(
        "-i",
        "--interval",
        type=int,
        default=1,
        help="""
        Time interval between each statistics sample, not used for pull model backend.
        """,
    )
    parser.add_argument(
        "-p",
        "--port",
        type=int,
        default=9000,
        help="""
        Listening port for prometheus polling.
        """,
    )
    parser.add_argument(
        "-b",
        "--backend",
        type=int,
        default=1,
        help="""
        Collector backend choices, 1: prometheus, 2: otlp.
        """
    )
    parser.add_argument(
        "--otlp-url",
        type=str,
        default="http://localhost:4317",
        help="""
        OTLP URL, required for OTLP backend, default to http://localhost:4317.
        """
    )
    args = parser.parse_args()

    if not os.path.exists(args.sock_prefix):
        print("Please provide a valid --sock-prefix option")
        # sock_path = sock_prefix + <app name> + "/dpdk_telemetry.v2"
        raise SystemExit

    initialize_sock_dict(args.sock_prefix, sock_dict)

    if args.backend == 1:
        start_http_server(args.port)
        REGISTRY.register(PrometheusCollector(sock_dict))
    elif args.backend == 2:
        resource = Resource(attributes={
            SERVICE_NAME: "dpdk-telemetry"
        })
        insecure = False
        if args.otlp_url.startswith("http://"):
            insecure = True
        reader = PeriodicExportingMetricReader(
            OTLPMetricExporter(endpoint=args.otlp_url, insecure=insecure),
            export_interval_millis=args.interval*1000
        )
        provider = MeterProvider(resource=resource, metric_readers=[reader])
        metrics.set_meter_provider(provider)
        meter = metrics.get_meter("dpdk.stats")
        otlp = OtlpCollector(sock_dict)
        meter.create_observable_counter(
            "dpdk.stats",
            callbacks=[otlp.dpdk_telemetry_callback],
            description="DPDK Telemetry"
        )

    # watch for sub-dir creation/deletion under sock_prefix
    # Create an observer and attach the event handler
    event_handler = SocketEventHandler(sock_dict)
    observer = Observer()
    observer.schedule(event_handler, args.sock_prefix, recursive=False)

    # Start the observer
    observer.start()

    def term_handler(signum, frame):
        logging.info("SIGTERM detected, raise KeyboardInterrupt")
        raise KeyboardInterrupt

    # Setup SIGTERM handler
    signal.signal(signal.SIGTERM, term_handler)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("Keyboardinterrupt detected")
        observer.stop()

    observer.join()


if __name__ == "__main__":
    main()
