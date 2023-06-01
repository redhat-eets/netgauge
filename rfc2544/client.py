from __future__ import print_function
import logging
import argparse
import requests

def actionGetResult(args):
    response = requests.get('http://' + args.server_addr + ":" + str(args.server_port) + "/result")
    if not response.isResultAvailable:
        print("test result not avalable.")
        return
    print("port %s rx_pps: %.2f" %(response.stats[0].port, response.stats[0].rx_pps))
    print("port %s rx_latency_average: %.2f" %(response.stats[0].port, response.stats[0].rx_latency_average))
    print("port %s rx_pps: %.2f" %(response.stats[1].port, response.stats[1].rx_pps))
    print("port %s rx_latency_average: %.2f" %(response.stats[1].port, response.stats[1].rx_latency_average))

def actionStartTrafficgen(args):
    json_data = {
        'l3': l3,
        'device_pairs': args.device_pairs,
        'search_runtime': args.search_runtime,
        'validation_runtime': args.validation_runtime,
        'num_flows': args.num_flows,
        'frame_size': args.frame_size,
        'max_loss_pct': args.max_loss_pct,
        'sniff_runtime': args.sniff_runtime,
        'search_granularity': args.search_granularity,
        'rate_tolerance': args.rate_tolerance,
        'runtime_tolerance': args.runtime_tolerance,
        'negative_packet_loss': args.negative_packet_loss,
        'rate_tolerance_failure': args.rate_tolerance_failure,
        'binary_search_extra_args': [],
    }
    response = requests.post('http://' + args.server_addr + ":" + str(args.server_port) + "/trafficgen/start", json=json_data)
    print("start trafficgen: %s" % ("success" if response.success else "fail"))

def actionStopTrafficgen(args):
    response = requests.get('http://' + args.server_addr + ":" + str(args.server_port) + "/trafficgen/stop")
    print("stop trafficgen: %s" % ("success" if response.success else "fail"))

def actionStatus(args):
    response = requests.get('http://' + args.server_addr + ":" + str(args.server_port) + "/trafficgen/running")
    print("trafficgen is currently %s running" %("" if response.isTrafficgenRunning else "not"))
    response = requests.get('http://' + args.server_addr + ":" + str(args.server_port) + "/result/available")
    print("test result is avalable: %s" % ("yes" if response.isResultAvailable else "no"))

def actionGetMac(args):
    response = requests.get('http://' + args.server_addr + ":" + str(args.server_port) + "/maclist")
    print("This trafficgen mac list: %s" %(response.macList))

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
    else:
        print("invalid action: %s" %(args.action))


if __name__ == '__main__':
    global l3
    l3 = False
    logging.basicConfig()
    parser = argparse.ArgumentParser(description='Trafficgen client')
    parser.add_argument('action',
                        help='specify what action the server will take',
                        choices=['start', 'stop', 'status', 'get-result', 'get-mac']
                        )
    parser.add_argument('--frame-size',
                        dest='frame_size',
                        help='L2 frame size in bytes',
                        default=64,
                        type=int
                        )
    parser.add_argument('--num-flows',
                        dest='num_flows',
                        help='number of unique network flows',
                        default=1,
                        type = int,
                        )
    parser.add_argument('--search-runtime',
                        dest='search_runtime',
                        default=10,
                        help='test duration in seconds for each search iteration',
                        type=int
                        )
    parser.add_argument('--validation-runtime',
                        dest='validation_runtime',
                        help='test duration in seconds during final validation',
                        default=30,
                        type = int
                        )
    parser.add_argument('--sniff-runtime',
                        dest='sniff_runtime',
                        help='test duration in seconds during sniff phase',
                        default = 3,
                        type = int
                        )
    parser.add_argument('--max-loss-pct',
                        dest='max_loss_pct',
                        help='maximum percentage of packet loss',
                        default=0.002,
                        type = float
                        )
    parser.add_argument('--device-pairs',
                        dest='device_pairs',
                        help='list of device pairs in the form A:B[,C:D][,E:F][,...]',
                        default="0:1"
                        )
    parser.add_argument('--server-addr',
                        dest='server_addr',
                        help='trafficgen server address',
                        required=True
                        )
    parser.add_argument('--server-port',
                        dest='server_port',
                        help='trafficgen server port',
                        type = int,
                        required=True
                        )
    parser.add_argument('--search-granularity',
                        dest="search_granularity",
                        default=5.0,
                        type = float,
                        help="the search granularity in percent of throughput"
                        )
    parser.add_argument('--rate-tolerance',
                        dest="rate_tolerance",
                        default=50,
                        type = int,
                        help="the rate tolerance"
                        )
    parser.add_argument('--runtime-tolerance',
                        dest="runtime_tolerance",
                        default=50,
                        type = int,
                        help="the runtime tolerance"
                        )
    parser.add_argument('--negative-packet-loss',
                        dest="negative_packet_loss",
                        default='fail',
                        type = str,
                        help="negative packet loss"
                        )
    parser.add_argument('--rate-tolerance-failure',
                        dest="rate_tolerance_failure",
                        default='fail',
                        type = str,
                        help="rate tolerance failure"
                        )
    args = parser.parse_args()
    run(args)
