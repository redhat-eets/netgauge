package main

import (
	"os"
	"log"
	"regexp"

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
