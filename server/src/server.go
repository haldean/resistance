package main

import (
	"resistance"
	"time"
)

func main() {
	g := resistance.Game{}
	g.AddPlayer(resistance.NewTestPlayer("one"))
	g.AddPlayer(resistance.NewTestPlayer("two"))
	g.Broadcast("test message")

	// wait for everything to get cleaned up
	time.Sleep(100 * time.Millisecond)
}
