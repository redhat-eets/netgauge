package main

import (
	"net/http"

	"github.com/gin-gonic/gin"
)

type testpmd_status struct {
	Status string `json:"status"`
}

func setup_rest_endpoint(router *gin.Engine) {
	router.GET("/status", getStatus)
}

func getStatus(c *gin.Context) {
	c.IndentedJSON(http.StatusOK, testpmd_status{Status: "ok"})
}
