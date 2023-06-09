package main

import (
	"testing"

	"context"
	"log"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/gin-gonic/gin"
	"golang.org/x/sys/unix"
)

func TestSchedSetaffinity(t *testing.T) {

	var newMask unix.CPUSet
	newMask.Set(0)

	if err := unix.SchedSetaffinity(0, &newMask); err != nil {
		t.Errorf("SchedSetaffinity: %v", err)
	}
	newMask.Zero()
	if err := unix.SchedGetaffinity(0, &newMask); err != nil {
		t.Errorf("SchedGetaffinity: %v", err)
	}
	if !newMask.IsSet(0) {
		t.Failed()
	}
}

func TestRestAPI(t *testing.T) {
	router := gin.Default()
	router.GET("/", func(c *gin.Context) {
		c.String(http.StatusOK, "Welcome Gin Server")
	})

	srv := &http.Server{
		Addr:    ":8080",
		Handler: router,
	}

	done := make(chan int)

	go func() {
		// service connections
		if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			t.Errorf("listen: %s\n", err)
		}
		done <- 1
	}()

	sigs := make(chan os.Signal, 1)
	signal.Notify(sigs, syscall.SIGINT, os.Interrupt, syscall.SIGTERM)
	<-sigs
	log.Println("Shutdown Server ...")
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()
	if err := srv.Shutdown(ctx); err != nil {
		t.Errorf("Server Shutdown: %s\n", err)
	}
	select {
	case <-ctx.Done():
		log.Println("timeout of 5 seconds.")
	case <-done:
		log.Println("rest server finished.")
	}
}
