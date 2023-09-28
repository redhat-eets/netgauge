package main

import (
	"context"
	"flag"
	"log"
	"net/http"
	"os"
	"os/signal"
	"regexp"
	"strconv"
	"strings"
	"syscall"
	"time"

	"github.com/gin-gonic/gin"
	"golang.org/x/sys/unix"
)

func (p *pciArray) String() string {
	return strings.Join(*p, " ")
}

func (p *pciArray) Set(value string) error {
	// normalize pci address to start with 0000: prefix
	pci := normalizePci(value)
	if _, err := os.Stat(pciDeviceDir + pci); os.IsNotExist(err) {
		log.Fatalf("invalid pci %s", value)
	}
	*p = append(*p, pci)
	return nil
}

func main() {
	httpPort := flag.Int("http-port", 9000, "http port")
	autoStart := flag.Bool("auto", false, "auto start in io mode")
	queues := flag.Int("queues", 1, "number of rxq/txq")
	ring := flag.Int("ring-size", 2048, "ring size")
	var pci pciArray
	flag.Var(&pci, "pci", "pci address, can specify multiple times")
	testpmdPath := flag.String("testpmd-path", "testpmd", "if not in PATH, specify the testpmd location")
	flag.Parse()
	// if pci not specified on CLI, try enviroment vars
	if len(pci) == 0 {
		r := regexp.MustCompile(`PCIDEVICE_OPENSHIFT_IO_[A-Za-z0-9_]+$`)
		for _, e := range os.Environ() {
			pair := strings.SplitN(e, "=", 2)
			if r.Match([]byte(pair[0])) && !strings.HasSuffix(pair[0], "_INFO") {
				pci = append(pci, normalizePci(pair[1]))
			}
		}
	}
	// if still have no pci info, then exit
	if len(pci) == 0 {
		log.Fatalf("pci address not provided\n")
	}

	cset := removeSiblings(getProcCpuset())
	mgmt_cpu := firstCpuFromCpuset(cset)
	var newMask unix.CPUSet
	newMask.Set(mgmt_cpu)

	// setaffinity on current process
	if err := unix.SchedSetaffinity(0, &newMask); err != nil {
		log.Fatalf("SchedSetaffinity: %v", err)
	}

	pTestpmd = &testpmd{}
	if err := pTestpmd.init(cset, mgmt_cpu, pci, *queues, *ring, *testpmdPath); err != nil {
		log.Fatalf("%v", err)
	}
	if *autoStart {
		log.Printf("auto start io mode\n")
		if err := pTestpmd.ioMode(); err != nil {
			log.Fatal(err)
		}
	}

	done := make(chan int)
	gin.SetMode(gin.ReleaseMode)
	router := gin.Default()
	setup_rest_endpoint(router)
	addr := ":" + strconv.Itoa(*httpPort)
	log.Printf("server addr: %s\n", addr)
	srv := &http.Server{
		Addr:    addr,
		Handler: router,
	}
	go func() {
		// service connections
		if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			log.Fatalf("listen: %s\n", err)
		}
		done <- 1
	}()

	sigs := make(chan os.Signal, 1)
	signal.Notify(sigs, syscall.SIGINT, os.Interrupt, syscall.SIGTERM)
	<-sigs
	log.Println("shutdown server ...")
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()
	if err := srv.Shutdown(ctx); err != nil {
		log.Fatal("server shutdown:", err)
	}
	select {
	case <-ctx.Done():
		log.Println("timeout of 5 seconds.")
	case <-done:
		log.Println("rest server finished.")
	}
	pTestpmd.terminate()

	pTestpmd.releaseHugePages()
}
