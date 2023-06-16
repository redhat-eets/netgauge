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
