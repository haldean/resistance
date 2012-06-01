#!/bin/sh

dot server-state-machine.dot -Teps -O -Nfontname="Helvetica" -Efontname="Helvetica" -Efontsize=10 -Nfontsize=11
epspdf server-state-machine.dot.eps
rm server-state-machine.dot.eps
