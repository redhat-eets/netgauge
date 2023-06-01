"""
|------------------------------------------------------------------------------|
|                                                                              |
|    Filename: rest.py                                                         |
|     Authors: Jianzhu Zhang                                                   |
|              Daniel Kostecki                                                 |
| Description: REST API implementation for netgauge, based off previous gRPC   |
|              implementation.                                                 |
|                                                                              |
|------------------------------------------------------------------------------|
"""

from flask import Flask, jsonify, request
import json
from marshmallow import EXCLUDE
import os.path
import psutil
import re
from rest_schema import ResultSchema, StartSchema, StartSchemal3, PortSchema
import subprocess
import sys

sys.path.append("/opt/trex/current/automation/trex_control_plane/interactive")
from trex.stl.api import *  # noqa: E402, F403
from trex_tg_lib import *  # noqa: E402, F403


app = Flask(__name__)


def checkIfProcessRunning(processName: str) -> bool:
    """Check if there is any running process that contains the given name processName.

    Args:
        processName(String): The name of the process

    Returns:
        Boolean: True if running, False otherwise
    """
    # Iterate over the all the running processes.
    for proc in psutil.process_iter():
        try:
            pinfo = proc.as_dict(attrs=["pid", "name", "status"])
            # Check if process name contains the given name string.
            if processName.lower() in pinfo["name"].lower():
                if "zombie" in pinfo["status"].lower():
                    os.waitpid(pinfo["pid"], os.WNOHANG)
                    continue
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    return False


def killProcessByName(processName: str) -> bool:
    """Kill all PIDs whose name contains the given processName.

    Args:
        processName(String): The name of the process

    Returns:
        Boolean: True on success, False otherwise
    """
    # Iterate over the all the running process
    for proc in psutil.process_iter():
        try:
            pinfo = proc.as_dict(attrs=["pid", "name"])
            # Check if process name contains the given name string.
            if processName.lower() in pinfo["name"].lower():
                p = psutil.Process(pinfo["pid"])
                p.terminate()
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            return False
    return True


class RestApi:
    @app.route("/trafficgen/running", methods=["GET"])
    def is_trafficgen_running() -> dict:
        """Endpoint to check for a running trafficgen via GET.

        Args:
            None

        Returns:
            dict: json wrapped boolean result of process running
        """
        return jsonify(checkIfProcessRunning("binary-search"))

    @app.route("/trafficgen/start", methods=["POST"])
    def start_trafficgen() -> dict:
        """Endpoint to start trafficgen via POST.

        Args:
            None, POST requires StartSchema or StartSchemal3 JSON

        Returns:
            dict: json wrapped boolean result of starting trafficgen
        """
        request_data = request.get_json()
        # If an instance is already running, kill it first
        if checkIfProcessRunning("binary-search"):
            if not killProcessByName("binary-search"):
                return jsonify(False)
        start_schema = StartSchema()
        result = start_schema.load(request_data)
        if result["l3"]:
            start_schema = StartSchemal3()
            result = start_schema.load(request_data)

        binary_search_command = ["./binary-search.py", "--traffic-generator=trex-txrx"]
        for field in result:
            if field == "send_teaching_warmup":
                binary_search_command.append("--" + field.replace("_", "-"))
            elif field in [
                "use_src_ip_flows",
                "use_dst_ip_flows",
                "use_src_mac_flows",
                "use_dst_mac_flows",
            ]:
                binary_search_command.append(
                    "--"
                    + field.replace("_", "-")
                    + "="
                    + str(int(result[field] == True))  # noqa: E712
                )
            elif field == "binary_search_extra_args":
                for extra_arg in result[field]:
                    binary_search_command.append(result[field][extra_arg])
            elif field == "l3":
                pass
            else:
                binary_search_command.append(
                    "--" + field.replace("_", "-") + "=" + str(result[field])
                )
        print(binary_search_command)
        subprocess.Popen(binary_search_command)

        if checkIfProcessRunning("binary-search"):
            return jsonify(True)
        else:
            return jsonify(False)

    @app.route("/trafficgen/stop", methods=["GET"])
    def stop_trafficgen() -> dict:
        """Endpoint to stop trafficgen via GET.

        Args:
            None

        Returns:
            dict: json wrapped boolean result of stopping trafficgen
        """
        return jsonify(killProcessByName("binary-search"))

    @app.route("/result/available", methods=["GET"])
    def isResultAvailable() -> dict:
        """Check if results are available via GET.

        Args:
            None

        Returns:
            dict: json wrapped boolean result
        """
        # If the result file is not present or the last trial did not pass,
        # then results are not available
        try:
            with open("binary-search.json") as f:
                data = json.load(f)
            result = data["trials"][-1]["result"]
            if result == "pass":
                return jsonify(True)
            else:
                return jsonify(False)
        except Exception:
            return jsonify(False)

    @app.route("/result", methods=["GET"])
    def get_result() -> dict:
        """Endpoint to fetch results via GET.

        Args:
            None

        Returns:
            dict: json wrapped dict result
        """
        pattern = re.compile("^[0-9]+$")
        result = {}
        try:
            with open("binary-search.json") as f:
                data = json.load(f)
            stats = data["trials"][-1]["stats"]
            for port in stats:
                if not pattern.match(port):
                    continue
                result_schema = ResultSchema()
                results = result_schema.load(stats[port], unknown=EXCLUDE)
                result[port] = results
        except Exception:
            # return an empty dict upon exception
            result = {}

        return jsonify(result)

    @app.route("/maclist", methods=["GET"])
    def getMacList():
        """Endpoint to get mac addresses via GET.

        Args:
            None

        Returns:
            dict: json wrapped string list of macs
        """
        macList = ""
        try:
            c = STLClient(server="localhost")  # noqa: F405
            c.connect()
            port_info = c.get_port_info(ports=[0, 1])
            port_schema = PortSchema()
            port_0 = port_schema.load(port_info[0], unknown=EXCLUDE)
            port_1 = port_schema.load(port_info[1], unknown=EXCLUDE)
            macList = port_0["hw_mac"] + "," + port_1["hw_mac"]
        except TRexError:  # noqa: F405
            macList = ""
        finally:
            c.disconnect()
            return jsonify(macList)


def create_app():
    return app
