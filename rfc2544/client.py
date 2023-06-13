from __future__ import print_function
import logging
import argparse
import requests
import json
import datetime
import time


def actionGetResult(args, returnResults=False):
    response = requests.get(
        "http://" + args.server_addr + ":" + str(args.server_port) + "/result"
    )
    if not response.json():
        print("test result not avalable.")
        return
    if not returnResults:
        print(response.json())
        for port in response.json():
            print("port %s rx_pps: %.2f" % (port, response.json()[port]["rx_pps"]))
            print(
                "port %s rx_latency_average: %.2f"
                % (port, response.json()[port]["rx_latency_average"])
            )
    else:
        return response.json()


def actionStartTrafficgen(args, returnResults=False):
    json_data = {
        "l3": l3,
        "device_pairs": args.device_pairs,
        "search_runtime": args.search_runtime,
        "validation_runtime": args.validation_runtime,
        "num_flows": args.num_flows,
        "frame_size": args.frame_size,
        "max_loss_pct": args.max_loss_pct,
        "sniff_runtime": args.sniff_runtime,
        "search_granularity": args.search_granularity,
        "rate_tolerance": args.rate_tolerance,
        "runtime_tolerance": args.runtime_tolerance,
        "negative_packet_loss": args.negative_packet_loss,
        "rate_tolerance_failure": args.rate_tolerance_failure,
        "binary_search_extra_args": [],
    }
    response = requests.post(
        "http://"
        + args.server_addr
        + ":"
        + str(args.server_port)
        + "/trafficgen/start",
        json=json_data,
    )
    if not returnResults:
        print("start trafficgen: %s" % ("success" if response.json() else "fail"))
    else:
        return response.json()


def actionStopTrafficgen(args, returnResults=False):
    response = requests.get(
        "http://" + args.server_addr + ":" + str(args.server_port) + "/trafficgen/stop"
    )
    if not returnResults:
        print("stop trafficgen: %s" % ("success" if response.json() else "fail"))
    else:
        return response.json()


def actionStatus(args, returnResults=False):
    results = {}
    response = requests.get(
        "http://"
        + args.server_addr
        + ":"
        + str(args.server_port)
        + "/trafficgen/running"
    )
    if not returnResults:
        print("trafficgen is currently%s running" % ("" if response.json() else " not"))
    else:
        results["running"] = response.json()

    response = requests.get(
        "http://" + args.server_addr + ":" + str(args.server_port) + "/result/available"
    )
    if not returnResults:
        print("test result is avalable: %s" % ("yes" if response.json() else "no"))
    else:
        results["available"] = response.json()

    if returnResults:
        return results


def actionGetMac(args, returnResults=False):
    response = requests.get(
        "http://" + args.server_addr + ":" + str(args.server_port) + "/maclist"
    )
    if not returnResults:
        print("This trafficgen mac list: %s" % (response.json()))
    else:
        return response.json()


def actionAuto(args):
    json_data = {}
    if args.config:
        f = open(args.config)
        json_data = json.load(f)

    if actionStatus(args, returnResults=True)["running"]:
        assert actionStopTrafficgen(args, returnResults=True) is True

    overwriteArgs(args, json_data)
    assert actionStartTrafficgen(args, returnResults=True) is True

    # Loop until timeout, checking for results
    timeout_time = datetime.datetime.now() + datetime.timedelta(0, 60 * args.timeout)

    while True:
        if datetime.datetime.now() > timeout_time:
            print("Timed out waiting for results")
            exit(1)
        time.sleep(5)
        status = actionStatus(args, returnResults=True)
        if status["available"] and not status["running"]:
            break

    results = actionGetResult(args, returnResults=True)
    print(results)


def overwriteArgs(args, json_data):
    parser = argparse.ArgumentParser()
    for field in json_data:
        parser.add_argument("--" + field, type=type(json_data[field]))
        parser.parse_args(args=["--" + field, str(json_data[field])], namespace=args)


def run(args):
    if args.action == "start":
        actionStartTrafficgen(args)
    elif args.action == "stop":
        actionStopTrafficgen(args)
    elif args.action == "status":
        actionStatus(args)
    elif args.action == "get-result":
        actionGetResult(args)
    elif args.action == "get-mac":
        actionGetMac(args)
    elif args.action == "auto":
        actionAuto(args)
    else:
        print("invalid action: %s" % (args.action))


if __name__ == "__main__":
    global l3
    l3 = False
    logging.basicConfig()
    parser = argparse.ArgumentParser(description="Trafficgen client")
    parser.add_argument(
        "action",
        help="specify what action the server will take",
        choices=["start", "stop", "status", "get-result", "get-mac", "auto"],
    )
    parser.add_argument(
        "--frame-size",
        dest="frame_size",
        help="L2 frame size in bytes",
        default=64,
        type=int,
    )
    parser.add_argument(
        "--num-flows",
        dest="num_flows",
        help="number of unique network flows",
        default=1,
        type=int,
    )
    parser.add_argument(
        "--search-runtime",
        dest="search_runtime",
        default=10,
        help="test duration in seconds for each search iteration",
        type=int,
    )
    parser.add_argument(
        "--validation-runtime",
        dest="validation_runtime",
        help="test duration in seconds during final validation",
        default=30,
        type=int,
    )
    parser.add_argument(
        "--sniff-runtime",
        dest="sniff_runtime",
        help="test duration in seconds during sniff phase",
        default=3,
        type=int,
    )
    parser.add_argument(
        "--max-loss-pct",
        dest="max_loss_pct",
        help="maximum percentage of packet loss",
        default=0.002,
        type=float,
    )
    parser.add_argument(
        "--device-pairs",
        dest="device_pairs",
        help="list of device pairs in the form A:B[,C:D][,E:F][,...]",
        default="0:1",
    )
    parser.add_argument(
        "--server-addr",
        dest="server_addr",
        help="trafficgen server address",
        required=True,
    )
    parser.add_argument(
        "--server-port",
        dest="server_port",
        help="trafficgen server port",
        type=int,
        required=True,
    )
    parser.add_argument(
        "--search-granularity",
        dest="search_granularity",
        default=5.0,
        type=float,
        help="the search granularity in percent of throughput",
    )
    parser.add_argument(
        "--rate-tolerance",
        dest="rate_tolerance",
        default=50,
        type=int,
        help="the rate tolerance",
    )
    parser.add_argument(
        "--runtime-tolerance",
        dest="runtime_tolerance",
        default=50,
        type=int,
        help="the runtime tolerance",
    )
    parser.add_argument(
        "--negative-packet-loss",
        dest="negative_packet_loss",
        default="fail",
        type=str,
        help="negative packet loss",
    )
    parser.add_argument(
        "--rate-tolerance-failure",
        dest="rate_tolerance_failure",
        default="fail",
        type=str,
        help="rate tolerance failure",
    )
    parser.add_argument(
        "--config", dest="config", type=str, help="path to the config yaml"
    )
    parser.add_argument(
        "--timeout",
        dest="timeout",
        default=10,
        type=int,
        help="timeout of auto in minutes",
    )
    args = parser.parse_args()
    run(args)
