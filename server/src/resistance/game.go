package resistance

type Command struct {
	Msg string
	Sender *Player
}

type Game struct {
	players []*Player
	Queue chan *Command
}

func NewGame() *Game {
	g := Game{Queue: make(chan *Command, 16)}
	return g
}

func (game *Game) AddPlayer(p *Player) {
	game.players = append(game.players, p)
}

func (game *Game) Broadcast(msg string) {
	for _, p := range game.players {
		go p.Send(msg)
	}
}

func (game *Game) Loop() {
	for {
		cmd := <-game.Queue
		switch cmd.Msg {
		case "toggleready":
			cmd.Player.ToggleReady()
		}
	}
}
