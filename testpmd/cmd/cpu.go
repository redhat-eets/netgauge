package main

import (
	"fmt"
	"log"
	"os"
	"regexp"
	"strings"

	"k8s.io/kubernetes/pkg/kubelet/cm/cpuset"
)

func getProcCpuset() cpuset.CPUSet {
	content, err := os.ReadFile("/proc/self/status")
	if err != nil {
		log.Fatal(err)
	}
	r := regexp.MustCompile(`Cpus_allowed_list:\s*([0-9,-]*)\r?\n`)
	cpus := r.FindStringSubmatch(string(content))[1]
	cset, err := cpuset.Parse(cpus)
	if err != nil {
		log.Fatal(err)
	}
	return cset
}

func firstCpuFromCpuset(cset cpuset.CPUSet) int {
	return cset.List()[0]
}

func removeSiblings(cset cpuset.CPUSet) cpuset.CPUSet {
	var cores []int
	visited := make(map[int]int)
	for _, cpu := range cset.List() {
		if _, ok := visited[cpu]; ok {
			continue
		}
		path := fmt.Sprintf("/sys/devices/system/cpu/cpu%d/topology/thread_siblings_list", cpu)
		content, err := os.ReadFile(path)
		if err != nil {
			log.Fatal(err)
		}
		siblingSet, err := cpuset.Parse(strings.TrimRight(string(content), "\r\n"))
		if err != nil {
			log.Fatal(err)
		}
		siblings := siblingSet.List()
		cores = append(cores, cpu)
		for _, sibling := range siblings {
			visited[sibling] = 1
		}
	}
	fmt.Printf("cpu list after removing siblings: %v\n", cores)
	return cpuset.New(cores...)
}
