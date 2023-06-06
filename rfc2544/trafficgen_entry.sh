#!/bin/bash
# env: peer_mac_west peer_mac_east validation_seconds search_seconds sniff_seconds loss_ratio flows frame_size

validation_seconds=${validation_seconds:-30}
search_seconds=${search_seconds:-10}
sniff_seconds=${sniff_seconds:-10}
loss_ratio=${loss_ratio:-0.002}
flows=${flows:-1024}
frame_size=${frame_size:-64}
rate=${rate:-25}
steady_rate=${steady_rate:-0}
page_prefix="rfc2544_trex"
pciDeviceDir="/sys/bus/pci/devices"
vf_extra_opt=${vf_extra_opt:-"--no-promisc"}
trex_extra_opt=${trex_extra_opt:-""}   # for mlx use "--mlx5-so"
pciArray=()

function print_help() {
    echo "Availble arguments: start | server | debug | help"
    echo "start - start the RFC2544 run"
    echo "server - start the rest api service and wait for rest request"
    echo "debug - only start the trex server in foreground"
}

function convert_number_range() {
    # converts a range of cpus, like "1-3,5" to a list, like "1,2,3,5"
    local cpu_range=$1
    local cpus_list=""
    local cpus=""
    for cpus in `echo "${cpu_range}" | sed -e 's/,/ /g'`; do
        if echo "${cpus}" | grep -q -- "-"; then
            cpus=`echo ${cpus} | sed -e 's/-/ /'`
            cpus=`seq ${cpus} | sed -e 's/ /,/g'`
        fi
        for cpu in ${cpus}; do
            cpus_list="${cpus_list},${cpu}"
        done
    done
    cpus_list=`echo ${cpus_list} | sed -e 's/^,//'`
    echo "${cpus_list}"
}

function sigfunc() {
    pid=`pgrep waitress-serve`
    [ -z ${pid} ] || kill ${pid}
    pid=`pgrep binary-search`
    [ -z ${pid} ] || kill ${pid}
    tmux kill-session -t trex 2>/dev/null
    rm -rf /dev/hugepages/${page_prefix}*
    exit 0
}

trap sigfunc SIGTERM SIGINT SIGUSR1


if [ "$1" == "help" ]; then
    print_help
    exit 0
elif [[ "$1" =~ ^(server|start|debug)$ ]]; then
    if [ -z "${pci_list}" ]; then
        # is this a openshift sriov pod?
        pci_list=$(env | sed -n -r -e 's/PCIDEVICE.*=(.*)/\1/p' | tr '\n' ',')
        if [ -z "${pci_list}" ]; then
            echo "need env var: pci_list"
            exit 1
        fi
    fi

    for pci in $(echo ${pci_list} | sed -e 's/,/ /g'); do
        if [[ ${pci} != 0000:* ]]; then
            pci=0000:${pci}
        fi
        pciArray+=(${pci})
    done

    # how many devices?
    number_of_devices=$(echo ${pci_list} | sed -e 's/,/ /g' | wc -w)
    if [ ${number_of_devices} -lt 2 ]; then
        echo "need at least 2 pci devices"
        exit 1
    fi
    # device_pairs in form of "0:1,2:3"
    index=0
    while [ ${index} -lt ${number_of_devices} ]; do
        if [ -z ${device_pairs} ]; then
            device_pairs="$((index)):$((index+1))"
        else
            device_pairs="${device_pairs},$((index)):$((index+1))"
        fi
        ((index+=2))
    done
    # only two peer mac address can be specified as gateway, if >2 pci slot is supplied, then fall back to io mode even and ignore the peer mac address
    if ((index > 2)); then
        l3=0
    elif [[ -z "${peer_mac_west}" || -z "${peer_mac_east}" ]]; then
        l3=0
    else
        l3=1
    fi
else
    print_help
    exit 1
fi

cd /root/tgen
#pciArray is set above, or we can alway use the following line in stead
#read -a pciArray <<< $(echo ${pci_list} | sed -e 's/,/ /g')
export NIC1=${pciArray[0]}
export NIC2=${pciArray[1]}
isolated_cpus=$(cat /proc/self/status | grep Cpus_allowed_list: | cut -f 2)
read -a cpuArray <<< $(convert_number_range ${isolated_cpus} | sed -e 's/,/ /g')
export master_cpu=${cpuArray[0]}
export latency_cpu=${cpuArray[1]}
#client_cpu is used to run binary search code
client_cpu=${cpuArray[2]}
cpuArray=("${cpuArray[@]:3}")
workerCPUs=${#cpuArray[@]}
export worker_cpu=$(echo ${cpuArray[@]} | sed -e 's/ /,/g')
export numa_node=$(cat ${pciDeviceDir}/${NIC1}/numa_node)

yaml_file=/tmp/trex_cfg.yaml
envsubst < trex_cfg.yaml.tmpl > ${yaml_file}

pushd /opt/trex/current

rm -rf /dev/hugepages/${page_prefix}*
trex_server_cmd="./t-rex-64 -i -c ${workerCPUs} --no-ofed-check --checksum-offload --cfg ${yaml_file} --iom 0 -v 4 --prefix ${page_prefix} ${trex_extra_opt}"
echo "run trex server cmd: ${trex_server_cmd}"
echo "trex yaml:"
echo "-------------------------------------------------------------------"
cat ${yaml_file}
echo "-------------------------------------------------------------------"
rm -fv /tmp/trex.server.out

taskset -pc ${client_cpu} $$

if [[ "$1" == "debug" ]]; then
    # this should take the foreground so the container does not terminate
    taskset -c ${client_cpu} ${trex_server_cmd}
    exit 0
fi

taskset -c ${client_cpu} tmux new-session -d -n server -s trex "bash -c '${trex_server_cmd} | taskset -c ${client_cpu} tee /tmp/trex.server.out'"
popd

count=60
num_ports=0
while [ ${count} -gt 0 -a ${num_ports} -lt 2 ]; do
    sleep 1
    num_ports=`netstat -tln | grep -E :4500\|:4501 | wc -l`
    ((count--))
done
if [ ${num_ports} -eq 2 ]; then
    echo "trex-server is ready"
else
    echo "ERROR: trex-server could not start properly"
    cat /tmp/trex.server.out
    exit 1
fi

if [ "$1" == "start" ]; then
    dst_mac_opt=""
    if (( l3 == 1)); then
        dst_mac_opt="--dst-macs=${peer_mac_west},${peer_mac_east}"
    fi
    for size in $(echo ${frame_size} | sed -e 's/,/ /g'); do
        taskset -c ${client_cpu} ./binary-search.py \
            --traffic-generator=trex-txrx \
            --device-pairs=${device_pairs} \
            --active-device-pairs=${device_pairs} \
            --sniff-runtime=${sniff_seconds} \
            --search-runtime=${search_seconds} --validation-runtime=${validation_seconds} --max-loss-pct=${loss_ratio} \
            --traffic-direction=bidirectional --frame-size=${size} --num-flows=${flows} \
            --rate-tolerance-failure=fail --duplicate-packet-failure=retry-to-fail --negative-packet-loss=retry-to-fail \
            --send-teaching-warmup \
            --teaching-warmup-packet-type=generic \
            --teaching-warmup-packet-rate=10000 \
            --use-src-ip-flows=1 --use-dst-ip-flows=1 \
            --use-src-mac-flows=0 --use-dst-mac-flows=0 \
            --rate-unit=% --rate=${rate} \
            --one-shot=${steady_rate} \
            --rate-tolerance=10 --runtime-tolerance=10 \
            ${dst_mac_opt} ${vf_extra_opt}
    done
elif [ "$1" == "server" ]; then
    taskset -c ${client_cpu} waitress-serve --host=0.0.0.0 --port=8080 --call rest:create_app
fi

tmux kill-session -t trex 2>/dev/null
rm -rf /dev/hugepages/${page_prefix}*

exit 0

