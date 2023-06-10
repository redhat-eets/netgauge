package main

import (
	"net/http"

	"github.com/gin-gonic/gin"
)

type testpmd_status struct {
	FwdMode    string `json:"mode"`
	Running    bool   `json:"running"`
	FilePrefix string `json:"name"`
}

func setup_rest_endpoint(router *gin.Engine) {
	router.GET("/testpmd/status", getTestpmdStatus)
	router.POST("/testpmd/stop", stopTestpmd)
}

func getTestpmdStatus(c *gin.Context) {
	c.IndentedJSON(http.StatusOK, testpmd_status{FwdMode: pTestpmd.fwdMode,
		Running: pTestpmd.running, FilePrefix: pTestpmd.filePrefix})
}

func stopTestpmd(c *gin.Context) {
	if err := pTestpmd.stop(); err != nil {
		c.IndentedJSON(http.StatusExpectationFailed, gin.H{"message": "Testpmd not working properly"})
		return
	}
	c.IndentedJSON(http.StatusOK, testpmd_status{FwdMode: pTestpmd.fwdMode,
		Running: pTestpmd.running, FilePrefix: pTestpmd.filePrefix})
}
