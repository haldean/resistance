package main

import (
	"fmt"
	"time"
)

type Player struct {
	socket chan string
	isSpy  bool
}

type Game struct {
	players []*Player
}

func printMessages(name string, in chan string) {
	for {
		str := <-in
		fmt.Printf("Send to %s: %s\n", name, str)
	}
}

func NewTestPlayer(name string) *Player {
	p := new(Player)
	p.socket = make(chan string)
	go printMessages(name, p.socket)
	return p
}

func (p *Player) Send(msg string) {
	p.socket <- msg
}

func (game *Game) AddPlayer(p *Player) {
	game.players = append(game.players, p)
}

func (game *Game) Broadcast(msg string) {
	for _, p := range game.players {
		go p.Send(msg)
	}
}

func main() {
	g := Game{}
	g.AddPlayer(NewTestPlayer("one"))
	g.AddPlayer(NewTestPlayer("two"))
	g.Broadcast("test message")

	// wait for everything to get cleaned up
	time.Sleep(100 * time.Millisecond)
}
