package main

import (
	"fmt"
	"reflect"
	"strconv"
	"strings"
)

func intToString(a []int, delim string) string {
	b := ""
	for _, v := range a {
		if len(b) > 0 {
			b += delim
		}
		b += strconv.Itoa(v)
	}
	return b
}

func portMask(ports int) string {
	var a uint8
	for i := 0; i < ports; i++ {
		a = a | (1 << i)
	}
	return fmt.Sprintf("%#x", a)
}

func isEmpty(value interface{}) bool {
	return value == nil || (reflect.ValueOf(value).Kind() == reflect.Ptr && reflect.ValueOf(value).IsNil())
}

func stripParams(command string) string {
	index := strings.IndexRune(command, ',')
	if index == -1 {
		return command
	}
	return command[:index]
}
