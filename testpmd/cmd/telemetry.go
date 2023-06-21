package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net"
	"strconv"
)

type telemetryResponse struct {
	response map[string]interface{} `json:"-"`
}

type sockConnetor struct {
	path       string
	maxLen     int
	connection net.Conn
}

const (
	sockPrefix           = "/var/run/dpdk/"
	sockSuffix           = "/dpdk_telemetry.v2"
	maxInitMessageLength = 2048
)

type initMessage struct {
	Version string `json:"version"`
	Pid     int    `json:"pid"`
	MaxLen  int    `json:"max_output_len"`
}

func newSockConnector(sockPath string) *sockConnetor {
	return &sockConnetor{
		path: sockPath,
	}
}

func (conn *sockConnetor) getMaxLen() error {
	buf := make([]byte, maxInitMessageLength)

	messageLength, err := conn.connection.Read(buf)
	if err != nil {
		return fmt.Errorf("failed to read InitMessage - %v", err)
	}

	var msg initMessage
	err = json.Unmarshal(buf[:messageLength], &msg)
	if err != nil {
		return fmt.Errorf("failed to unmarshal response - %v", err)
	}

	if msg.MaxLen == 0 {
		return fmt.Errorf("failed to read MaxLen information")
	}

	conn.maxLen = msg.MaxLen
	return nil
}

func (conn *sockConnetor) connect() error {
	connection, err := net.Dial("unixpacket", conn.path)
	if err != nil {
		conn.connection = nil
		return fmt.Errorf("failed to connect to the socket - %v", err)
	}

	conn.connection = connection
	err = conn.getMaxLen()
	return err
}

func (conn *sockConnetor) getConnection() error {
	if conn.connection == nil {
		if err := conn.connect(); err != nil {
			return err
		}
	}
	return nil
}

func (conn *sockConnetor) closeConnection() {
	if conn.connection != nil {
		conn.connection.Close()
		conn.connection = nil
	}
}

func (conn *sockConnetor) cmd(command string) ([]byte, error) {
	defer conn.closeConnection()
	if err := conn.getConnection(); err != nil {
		return nil, fmt.Errorf("failed to get connection to execute %v command - %v", command, err)
	}

	if _, err := conn.connection.Write([]byte(command)); err != nil {
		return nil, fmt.Errorf("failed to send '%v' command - %v", command, err)
	}

	buf := make([]byte, conn.maxLen)
	messageLength, err := conn.connection.Read(buf)
	if err != nil {
		return nil, fmt.Errorf("failed to read response of '%v' command - %v", command, err)
	}

	if messageLength == 0 {
		return nil, fmt.Errorf("got empty response during execution of '%v' command", command)
	}
	return buf[:messageLength], nil
}

func (conn *sockConnetor) processCommand(fullCommand string) (interface{}, error) {
	buf, err := conn.cmd(fullCommand)
	if err != nil {
		return nil, err
	}

	var parsedResponse map[string]interface{}
	err = json.Unmarshal(buf, &parsedResponse)
	if err != nil {
		return nil, fmt.Errorf("failed to unmarshall json response from '%v' - %v", fullCommand, err)
	}

	command := stripParams(fullCommand)
	value := parsedResponse[command]
	if isEmpty(value) {
		return nil, fmt.Errorf("got empty json on command: '%v'", command)

	}
	return value, nil
}

func (conn *sockConnetor) getPorts() ([]int, error) {
	output, err := conn.processCommand("/ethdev/list")
	if err != nil {
		return nil, err
	}

	portList := make([]int, 0)
	if olist, ok := output.([]interface{}); ok {
		for _, item := range olist {
			if port, ok := item.(float64); ok {
				portList = append(portList, int(port))
			} else {
				log.Printf("item type: %T", item)
			}
		}
	}
	return portList, nil
}

func (conn *sockConnetor) getFromAllPorts(command string) ([]interface{}, error) {
	ports, err := conn.getPorts()
	if err != nil {
		return nil, err
	}
	assembledData := make([]interface{}, 0)
	for _, port := range ports {
		data, err := conn.processCommand(command + "," + strconv.Itoa(port))
		if err != nil {
			return nil, err
		}
		assembledData = append(assembledData, data)
	}
	return assembledData, nil
}

func (conn *sockConnetor) getFromOnePort(command string, port string) (interface{}, error) {
	data, err := conn.processCommand(command + "," + port)
	if err != nil {
		return nil, err
	}
	return data, nil
}

func (conn *sockConnetor) getPortsInfo() ([]map[string]interface{}, error) {
	output, err := conn.getFromAllPorts("/ethdev/info")
	if err != nil {
		return nil, err
	}
	portInfo := make([]map[string]interface{}, 0)
	for _, item := range output {
		if itemMap, ok := item.(map[string]interface{}); ok {
			portInfo = append(portInfo, itemMap)
		}
	}
	return portInfo, nil
}

func (conn *sockConnetor) getPortInfo(port string) (map[string]interface{}, error) {
	output, err := conn.getFromOnePort("/ethdev/info", port)
	if err != nil {
		return nil, err
	}
	if portInfo, ok := output.(map[string]interface{}); ok {
		return portInfo, nil
	} else {
		return nil, fmt.Errorf("'%v' is not an map of [string]interface{}", output)
	}
}

func (conn *sockConnetor) getStatsByPort(port string) (map[string]interface{}, error) {
	output, err := conn.getFromOnePort("/ethdev/stats", port)
	if err != nil {
		return nil, err
	}
	if portStats, ok := output.(map[string]interface{}); ok {
		return portStats, nil
	} else {
		return nil, fmt.Errorf("'%v' is not an map of [string]interface{}", output)
	}
}

func (conn *sockConnetor) getStats() ([]map[string]interface{}, error) {
	output, err := conn.getFromAllPorts("/ethdev/stats")
	if err != nil {
		return nil, err
	}
	stats := make([]map[string]interface{}, 0)
	for _, item := range output {
		if itemMap, ok := item.(map[string]interface{}); ok {
			stats = append(stats, itemMap)
		}
	}
	return stats, nil
}
