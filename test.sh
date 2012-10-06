#!/bin/bash
# Test script for running with Travis CI

cd server
GOPATH=`pwd` go test -v resistance
