package resistance

import "fmt"

type Player struct {
	socket  chan string
	IsSpy   bool
	IsReady bool
}

func (p *Player) Send(msg string) {
	p.socket <- msg
}

func (p *Player) ToggleReady() {
	p.IsReady = !p.IsReady
}

func printMessages(name string, in chan string) {
	for {
		str := <-in
		fmt.Printf("Send to %s: %s\n", name, str)
	}
}

func NewTestPlayer(name string) *Player {
	p := new(Player)
	p.socket = make(chan string, 8)
	go printMessages(name, p.socket)
	return p
}
