package resistance

type Command struct {
	Msg    string
	Sender *Player
}

type Game struct {
	players []*Player
	Queue   chan *Command
	Quit    chan bool
	Running bool
}

func NewGame() *Game {
	g := Game{Queue: make(chan *Command, 16), Quit: make(chan bool)}
	return &g
}

// Player management

func (game *Game) AddPlayer(p *Player) {
	game.players = append(game.players, p)
}

func (game *Game) PlayerCount() int {
	return len(game.players)
}

func (game *Game) Broadcast(msg string) {
	for _, p := range game.players {
		go p.Send(msg)
	}
}

// Communication

func (game *Game) SendSpyStatus() {
	for _, p := range game.players {
		if p.IsSpy {
			go p.Send("SPY")
		} else {
			go p.Send("RESISTANCE")
		}
	}
}

func (game *Game) AllReady() bool {
	for _, p := range game.players {
		if !p.IsReady {
			return false
		}
	}
	return true
}

// Event loop

func (game *Game) HandleCommand(c *Command) {
	switch c.Msg {
	case "toggleready":
		c.Sender.ToggleReady()
	}
}

func (game *Game) Loop() {
	game.Running = true
	for game.Running {
		select {
		case cmd := <-game.Queue:
			game.HandleCommand(cmd)

		case _ = <-game.Quit:
			game.Running = false
		}
	}
}
