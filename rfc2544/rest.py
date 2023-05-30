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
    tx_l1_bps = fields.Float()
    tx_l2_bps = fields.Float()
    tx_pps = fields.Float()
    rx_l1_bps = fields.Float()
    rx_l2_bps = fields.Float()
    rx_pps = fields.Float()
    rx_latency_minimum = fields.Float()
    rx_latency_maximum = fields.Float()
    rx_latency_average = fields.Float()

class ResultDictSchema(Schema):
    results = fields.Dict(keys=fields.Int(), values=fields.Nested(ResultSchema))


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
            #portstats.port = port
            result_schema = ResultSchema()
            result_schema.dump(stats[port])
            result[port] = result_schema
    except:
        # return default value when something happens
        result = {}#rpc_pb2.Result()
    result_dict_schema = ResultDictSchema()
    return result_dict_schema.dump(result)

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
    if not bool(request_data["l3"]):
        subprocess.Popen(["./binary-search.py", "--traffic-generator=trex-txrx",
                        "--device-pairs=%s" % request_data["device_pairs"],
                        "--search-runtime=%d" % request_data["search_runtime"],
                        "--validation-runtime=%d" % request_data["validation_runtime"],
                        "--num-flows=%d" % request_data["num_flows"],
                        "--frame-size=%d" % request_data["frame_size"],
                        "--max-loss-pct=%f" % request_data["max_loss_pct"],
                        "--sniff-runtime=%d" % request_data["sniff_runtime"],
                        "--search-granularity=%f" % request_data["search_granularity"],
                        "--rate-tolerance=50",
                        "--runtime-tolerance=50",
                        "--negative-packet-loss=fail",
                        "--rate-tolerance-failure=fail"] + request_data["binary_search_extra_args"])
    else:
        subprocess.Popen(["./binary-search.py", "--traffic-generator=trex-txrx",
                        "--device-pairs=%s" % request_data["device_pairs"],
                        "--dst-macs=%s" % request_data["dst_macs"],
                        "--search-runtime=%d" % request_data["search_runtime"],
                        "--validation-runtime=%d" % request_data["validation_runtime"],
                        "--num-flows=%d" % request_data["num_flows"],
                        "--frame-size=%d" % request_data["frame_size"],
                        "--max-loss-pct=%f" % request_data["max_loss_pct"],
                        "--sniff-runtime=%d" % request_data["sniff_runtime"],
                        "--rate-tolerance=50",
                        "--runtime-tolerance=50",
                        "--negative-packet-loss=fail",
                        "--search-granularity=%f" % request_data["search_granularity"],
                        "--rate-tolerance-failure=fail"] + request_data["binary_search_extra_args"])
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
            macList = port_info[0]['hw_mac'] + ',' + port_info[1]['hw_mac']
        except TRexError as e:
            macList = ""
        finally:
            c.disconnect()
            return jsonify(macList)
