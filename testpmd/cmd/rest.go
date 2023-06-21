package main

import (
	"context"
	"encoding/json"
	"log"
	"net/http"

	"github.com/gin-gonic/gin"
	"github.com/qri-io/jsonschema"
)

type testpmd_status struct {
	FwdMode    string `json:"mode"`
	Running    bool   `json:"running"`
	FilePrefix string `json:"name"`
}

type testpmd_start struct {
	FwdMode string   `json:"mode"`
	PeerMac []string `json:"macs"`
}

type portMac struct {
	Port string `json:"port_id"`
	Mac  string `json:"mac_address"`
}

type portStats struct {
	Port          string  `json:"port_id"`
	InputPackets  float64 `json:"ipackets"`
	OutputPackets float64 `json:"opackets"`
	InputMissed   float64 `json:"imissed"`
}

type portInfo struct {
	Port        int    `json:"port_id"`
	Name        string `json:"name"`
	State       int    `json:"state"`
	Mac         string `json:"mac_addr"`
	Numa        int    `json:"numa_node"`
	Mtu         int    `json:"mtu"`
	Promiscuous int    `json:"promiscuous"`
}

var schemaStart = []byte(`{
    "type": "object",
    "properties": {
        "mode": {
            "type": "string"
        },
        "macs": {
          "type" : "array",
          "items" : {
			"type": "string"
		  }
        }
    },
    "required": ["mode", "macs"]
  }`)

func setup_rest_endpoint(router *gin.Engine) {
	router.GET("/testpmd/status", getTestpmdStatus)
	router.GET("/testpmd/mac/:id", getMacByID)
	router.GET("/testpmd/ports", listPorts)
	router.GET("/testpmd/stats/:id", getStatsByID)
	router.GET("/testpmd/portsinfo", getPortsInfo)
	router.POST("/testpmd/stop", stopTestpmd)
	router.POST("/testpmd/start", startTestpmd)
}

func getTestpmdStatus(c *gin.Context) {
	c.IndentedJSON(http.StatusOK, testpmd_status{FwdMode: pTestpmd.fwdMode,
		Running: pTestpmd.running, FilePrefix: pTestpmd.filePrefix})
}

func stopTestpmd(c *gin.Context) {
	if err := pTestpmd.stop(); err != nil {
		c.IndentedJSON(http.StatusInternalServerError, gin.H{"message": "Testpmd not working properly"})
		return
	}
	c.IndentedJSON(http.StatusOK, testpmd_status{FwdMode: pTestpmd.fwdMode,
		Running: pTestpmd.running, FilePrefix: pTestpmd.filePrefix})
}

func validateJson(schemaData []byte, data *[]byte) []jsonschema.KeyError {
	ctx := context.Background()
	rs := &jsonschema.Schema{}
	if err := json.Unmarshal(schemaData, rs); err != nil {
		pTestpmd.terminate()
		log.Fatal("unmarshal schema: " + err.Error())
	}
	errs, err := rs.ValidateBytes(ctx, *data)
	if err != nil {
		log.Println(err)
	}
	return errs
}

func startTestpmd(c *gin.Context) {
	var start_info testpmd_start
	data, err := c.GetRawData()
	if err != nil {
		log.Println(err)
		c.IndentedJSON(http.StatusInternalServerError, gin.H{"message": "no data"})
		return
	}
	errs := validateJson(schemaStart, &data)
	if len(errs) > 0 {
		log.Println(errs[0].Error())
		c.IndentedJSON(http.StatusBadRequest, gin.H{"message": "Invalid input"})
		return
	}
	if err := json.Unmarshal(data, &start_info); err != nil {
		log.Println(err)
		c.IndentedJSON(http.StatusBadRequest, gin.H{"message": "Invalid input"})
		return
	}
	for i, mac := range start_info.PeerMac {
		if err := pTestpmd.setPeerMac(i, mac); err != nil {
			c.IndentedJSON(http.StatusInternalServerError, gin.H{"message": "Testpmd not working properly"})
			return
		}
	}
	if err := pTestpmd.setFwdMode(start_info.FwdMode); err != nil {
		c.IndentedJSON(http.StatusInternalServerError, gin.H{"message": "Testpmd not working properly"})
		return
	}
	c.IndentedJSON(http.StatusOK, testpmd_status{FwdMode: pTestpmd.fwdMode,
		Running: pTestpmd.running, FilePrefix: pTestpmd.filePrefix})
}

func getMacByID(c *gin.Context) {
	id := c.Param("id")
	connector := newSockConnector(sockPrefix + pTestpmd.filePrefix + sockSurfix)
	portInfo, err := connector.getPortInfo(id)
	if err != nil {
		log.Println(err)
		c.IndentedJSON(http.StatusInternalServerError, gin.H{"message": "Telemetry not working"})
		return
	}
	if data, ok := portInfo["mac_addr"]; ok {
		if mac, ok := data.(string); ok {
			c.IndentedJSON(http.StatusOK, portMac{Port: id, Mac: mac})
		}
		return
	}
	c.IndentedJSON(http.StatusInternalServerError, gin.H{"message": "System got invalid data"})
}

func listPorts(c *gin.Context) {
	connector := newSockConnector(sockPrefix + pTestpmd.filePrefix + sockSurfix)
	ports, err := connector.getPorts()
	if err != nil {
		log.Println(err)
		c.IndentedJSON(http.StatusInternalServerError, gin.H{"message": "Telemetry not working"})
		return
	}
	c.IndentedJSON(http.StatusOK, ports)
}

func getStatsByID(c *gin.Context) {
	port := c.Param("id")
	connector := newSockConnector(sockPrefix + pTestpmd.filePrefix + sockSurfix)
	stats, err := connector.getStatsByPort(port)
	if err != nil {
		log.Println(err)
		c.IndentedJSON(http.StatusInternalServerError, gin.H{"message": "Telemetry not working"})
		return
	}
	var ipackets, imissed, opackets float64
	invalid := false
	if data, ok := stats["ipackets"]; ok {
		if ipackets, ok = data.(float64); !ok {
			invalid = true
			log.Printf("ipackets type: %T\n", stats["ipackets"])
		}
	} else {
		invalid = true
	}
	if data, ok := stats["imissed"]; ok {
		if imissed, ok = data.(float64); !ok {
			invalid = true
			log.Printf("ipackets type: %T\n", stats["ipackets"])
		}
	} else {
		invalid = true
	}
	if data, ok := stats["opackets"]; ok {
		if opackets, ok = data.(float64); !ok {
			invalid = true
			log.Printf("ipackets type: %T\n", stats["ipackets"])
		}
	} else {
		invalid = true
	}
	if invalid {
		c.IndentedJSON(http.StatusInternalServerError, gin.H{"message": "System got invalid data"})
	} else {
		c.IndentedJSON(http.StatusOK,
			portStats{Port: port,
				InputPackets:  ipackets,
				InputMissed:   imissed,
				OutputPackets: opackets})
	}
}

func getPortsInfo(c *gin.Context) {
	connector := newSockConnector(sockPrefix + pTestpmd.filePrefix + sockSurfix)
	info, err := connector.getPortsInfo()
	if err != nil {
		log.Println(err)
		c.IndentedJSON(http.StatusInternalServerError, gin.H{"message": "Telemetry not working"})
		return
	}

	invalid := false
	portsInfo := make([]portInfo, 0)
	var name, mac string
	var state, portID, mtu, promisc, numa float64
	var data interface{}
	var ok bool
	for _, item := range info {
		if data, ok = item["name"]; ok {
			if name, ok = data.(string); !ok {
				invalid = true
				log.Printf("name type: %T\n", item["name"])
				continue
			}
		} else {
			invalid = true
			continue
		}
		if data, ok = item["mac_addr"]; ok {
			if mac, ok = data.(string); !ok {
				invalid = true
				log.Printf("mac type: %T\n", item["mac"])
				continue
			}
		} else {
			invalid = true
			continue
		}
		if data, ok = item["state"]; ok {
			if state, ok = data.(float64); !ok {
				invalid = true
				log.Printf("state type: %T\n", item["state"])
				continue
			}
		} else {
			invalid = true
			continue
		}
		if data, ok = item["port_id"]; ok {
			if portID, ok = data.(float64); !ok {
				invalid = true
				log.Printf("port_id type: %T\n", item["port_id"])
				continue
			}
		} else {
			invalid = true
			continue
		}
		if data, ok = item["mtu"]; ok {
			if mtu, ok = data.(float64); !ok {
				invalid = true
				log.Printf("mtu type: %T\n", item["mtu"])
				continue
			}
		} else {
			invalid = true
			continue
		}
		if data, ok = item["promiscuous"]; ok {
			if promisc, ok = data.(float64); !ok {
				invalid = true
				log.Printf("promiscuous type: %T\n", item["state"])
				continue
			}
		} else {
			invalid = true
			continue
		}
		if data, ok = item["numa_node"]; ok {
			if numa, ok = data.(float64); !ok {
				invalid = true
				log.Printf("state type: %T\n", item["numa_node"])
				continue
			}
		} else {
			invalid = true
			continue
		}
		portsInfo = append(portsInfo,
			portInfo{
				Port:        int(portID),
				Name:        name,
				Mac:         mac,
				State:       int(state),
				Mtu:         int(mtu),
				Promiscuous: int(promisc),
				Numa:        int(numa)})
	}
	if invalid {
		c.IndentedJSON(http.StatusInternalServerError, gin.H{"message": "System got invalid data"})
	} else {
		c.IndentedJSON(http.StatusOK, portsInfo)
	}
}
