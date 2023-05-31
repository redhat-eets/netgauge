'''from concurrent import futures
import logging
import json
import psutil
import os.path
import subprocess
import re
import grpc
import rpc_pb2
import rpc_pb2_grpc
import argparse
import sys
sys.path.append('/opt/trex/current/automation/trex_control_plane/interactive')
from trex.stl.api import *
from trex_tg_lib import *
'''
import os.path
import psutil
import json
from flask import Flask, request, jsonify
import subprocess
import re
import sys
sys.path.append('/opt/trex/current/automation/trex_control_plane/interactive')
from trex.stl.api import *
from trex_tg_lib import *
from marshmallow import Schema, fields


app = Flask(__name__)


class ResultSchema(Schema):
    tx_l1_bps = fields.Float(required=True, error_messages={"required": "tx_l1_bps is required."})
    tx_l2_bps = fields.Float(required=True, error_messages={"required": "tx_l2_bps is required."})
    tx_pps = fields.Float(required=True, error_messages={"required": "tx_pps is required."})
    rx_l1_bps = fields.Float(required=True, error_messages={"required": "rx_l1_bps is required."})
    rx_l2_bps = fields.Float(required=True, error_messages={"required": "rx_l2_bps is required."})
    rx_pps = fields.Float(required=True, error_messages={"required": "rx_pps is required."})
    rx_latency_minimum = fields.Float(required=True, error_messages={"required": "rx_latency_minimum is required."})
    rx_latency_maximum = fields.Float(required=True, error_messages={"required": "rx_latency_maximum is required."})
    rx_latency_average = fields.Float(required=True, error_messages={"required": "rx_latency_average is required."})


class StartSchema(Schema):
    l3 = fields.Bool(required=True, error_messages={"required": "l3 is required."})
    device_pairs = fields.String(required=True, error_messages={"required": "device_pairs is required."})
    search_runtime = fields.Int(required=True, error_messages={"required": "search_runtime is required."})
    validation_runtime = fields.Int(required=True, error_messages={"required": "validation_runtime is required."})
    num_flows = fields.Int(required=True, error_messages={"required": "num_flows is required."})
    frame_size = fields.Int(required=True, error_messages={"required": "frame_size is required."})
    max_loss_pct = fields.Float(required=True, error_messages={"required": "max_loss_pct is required."})
    sniff_runtime = fields.Int(required=True, error_messages={"required": "sniff_runtime is required."})
    search_granularity = fields.Float(required=True, error_messages={"required": "search_granularity is required."})
    binary_search_extra_args = fields.List(fields.String(), required=False)


class StartSchemal3(StartSchema):
    dst_macs = fields.String(required=True, error_messages={"required": "dst_macs is required."})


class PortSchema(Schema):
    hw_mac = fields.String(required=True, error_messages={"required": "hw_mac is required."})

def checkIfProcessRunning(processName):
    '''
    Check if there is any running process that contains the given name processName.
    '''
    #Iterate over the all the running process
    for proc in psutil.process_iter():
        try:
            pinfo = proc.as_dict(attrs=['pid', 'name', 'status'])
            # Check if process name contains the given name string.
            if processName.lower() in pinfo['name'].lower():
                if 'zombie' in pinfo['status'].lower():
                    os.waitpid(pinfo['pid'], os.WNOHANG)
                    continue
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    return False

def killProcessByName(processName):
    '''
    kill all the PIDs whose name contains
    the given string processName
    '''
    #Iterate over the all the running process
    for proc in psutil.process_iter():
       try:
           pinfo = proc.as_dict(attrs=['pid', 'name'])
           # Check if process name contains the given name string.
           if processName.lower() in pinfo['name'].lower() :
               p = psutil.Process(pinfo['pid'])
               p.terminate()
       except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) :
           return False
    return True


@app.route('/trafficgen/running', methods=['GET'])
def is_trafficgen_running():
    return jsonify(checkIfProcessRunning("binary-search"))


#TODO: serialize
@app.route('/result', methods=['GET'])
def get_result():
    pattern = re.compile("^[0-9]+$")
    result = {} #rpc_pb2.Result()
    try:
        with open('binary-search.json') as f:
            data = json.load(f)
        stats = data["trials"][-1]["stats"]
        for port in stats:
            if not pattern.match(port):
                continue
            portstats = {}
            '''portstats["tx_l1_bps"] = stats[port]['tx_l1_bps']
            portstats["tx_l2_bps"] = stats[port]['tx_l2_bps']
            portstats["tx_pps"] = stats[port]['tx_pps']
            portstats["rx_l1_bps"] = stats[port]['rx_l1_bps']
            portstats["rx_l2_bps"] = stats[port]['rx_l2_bps']
            portstats["rx_pps"] = stats[port]['rx_pps']
            portstats["rx_latency_minimum"] = stats[port]['rx_latency_minimum']
            portstats["rx_latency_maximum"] = stats[port]['rx_latency_maximum']
            portstats["rx_latency_average"] = stats[port]['rx_latency_average']'''

            result_schema = ResultSchema()
            results = result_schema.load(stats[port], unknown = EXCLUDE)
            result[port] = results
    except:
        # return default value when something happens
        result = {}

    return jsonify(result)


@app.route('/trafficgen/stop', methods=['GET'])
def stop_trafficgen():
    return jsonify(killProcessByName("binary-search"))


@app.route('/result/available', methods=['GET'])
def isResultAvailable():
    '''
    #If result file is not present or last trial is not pass, then result is not available
    '''
    try:
        with open('binary-search.json') as f:
            data = json.load(f)
        result = data["trials"][-1]["result"]
        if result == 'pass':
            return jsonify(True)
        else:
            return jsonify(False)
    except:
        return jsonify(False)


#TODO: Serialize
@app.route('/trafficgen/start', methods=['POST'])
def start_trafficgen():
    request_data = request.get_json()
    # if an instance is already running, kill it first
    if checkIfProcessRunning("binary-search"):
        if not killProcessByName("binary-search"):
            return jsonify(False)
    start_schema = StartSchema()
    result = start_schema.load(request_data)
    if not result['l3']:
        subprocess.Popen(["./binary-search.py", "--traffic-generator=trex-txrx",
                        "--device-pairs=%s" % result["device_pairs"],
                        "--search-runtime=%d" % result["search_runtime"],
                        "--validation-runtime=%d" % result["validation_runtime"],
                        "--num-flows=%d" % result["num_flows"],
                        "--frame-size=%d" % result["frame_size"],
                        "--max-loss-pct=%f" % result["max_loss_pct"],
                        "--sniff-runtime=%d" % result["sniff_runtime"],
                        "--search-granularity=%f" % result["search_granularity"],
                        "--rate-tolerance=50",
                        "--runtime-tolerance=50",
                        "--negative-packet-loss=fail",
                        "--rate-tolerance-failure=fail"] + result["binary_search_extra_args"])
    else:
        start_schema_l3 = StartSchemal3()
        result = start_schema_l3.load(request_data)
        subprocess.Popen(["./binary-search.py", "--traffic-generator=trex-txrx",
                        "--device-pairs=%s" % result["device_pairs"],
                        "--dst-macs=%s" % result["dst_macs"],
                        "--search-runtime=%d" % result["search_runtime"],
                        "--validation-runtime=%d" % result["validation_runtime"],
                        "--num-flows=%d" % result["num_flows"],
                        "--frame-size=%d" % result["frame_size"],
                        "--max-loss-pct=%f" % result["max_loss_pct"],
                        "--sniff-runtime=%d" % result["sniff_runtime"],
                        "--rate-tolerance=50",
                        "--runtime-tolerance=50",
                        "--negative-packet-loss=fail",
                        "--search-granularity=%f" % result["search_granularity"],
                        "--rate-tolerance-failure=fail"] + result["binary_search_extra_args"])
    if checkIfProcessRunning("binary-search"):
        return jsonify(True)
    else:
        return jsonify(False)


@app.route('/maclist', methods=['GET'])
def getMacList():
        macList = ""
        try:
            c = STLClient(server = 'localhost')
            c.connect()
            port_info = c.get_port_info(ports = [0, 1])
            port_schema = PortSchema()
            port_0 = port_schema.load(port_info[0], unknown=EXCLUDE)
            port_1 = port_schema.load(port_info[1], unknown=EXCLUDE)
            macList = port_0['hw_mac'] + ',' + port_1['hw_mac']
        except TRexError as e:
            macList = ""
        finally:
            c.disconnect()
            return jsonify(macList)
