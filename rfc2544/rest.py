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
from trex.stl.api import *
from trex_tg_lib import *

app = Flask(__name__)

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

@app.route('/result', methods=['GET'])
def get_result():
    pattern = re.compile("^[0-9]+$")
    # NOTE: NOT COMPLETE


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


@app.route('/trafficgen/start', methods=['GET'])
def start_trafficgen():
    # if an instance is already running, kill it first
    if checkIfProcessRunning("binary-search"):
        if not killProcessByName("binary-search"):
            return jsonify(False)
    if not request.l3:
        subprocess.Popen(["./binary-search.py", "--traffic-generator=trex-txrx",
                        "--device-pairs=%s" % request.device_pairs,
                        "--search-runtime=%d" % request.search_runtime,
                        "--validation-runtime=%d" % request.validation_runtime,
                        "--num-flows=%d" % request.num_flows,
                        "--frame-size=%d" % request.frame_size,
                        "--max-loss-pct=%f" % request.max_loss_pct,
                        "--sniff-runtime=%d" % request.sniff_runtime,
                        "--search-granularity=%f" % request.search_granularity,
                        "--rate-tolerance=50",
                        "--runtime-tolerance=50",
                        "--negative-packet-loss=fail",
                        "--rate-tolerance-failure=fail"] + binary_search_extra_args)
    else:
        subprocess.Popen(["./binary-search.py", "--traffic-generator=trex-txrx",
                        "--device-pairs=%s" % request.device_pairs,
                        "--dst-macs=%s" % request.dst_macs,
                        "--search-runtime=%d" % request.search_runtime,
                        "--validation-runtime=%d" % request.validation_runtime,
                        "--num-flows=%d" % request.num_flows,
                        "--frame-size=%d" % request.frame_size,
                        "--max-loss-pct=%f" % request.max_loss_pct,
                        "--sniff-runtime=%d" % request.sniff_runtime,
                        "--rate-tolerance=50",
                        "--runtime-tolerance=50",
                        "--negative-packet-loss=fail",
                        "--search-granularity=%f" % request.search_granularity,
                        "--rate-tolerance-failure=fail"] + binary_search_extra_args)
    if checkIfProcessRunning("binary-search"):
        return rpc_pb2.Success(success=True)
    else:
        return rpc_pb2.Success(success=False)


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