package main

import (
	"testing"

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
