package resistance

import ()

type Command struct {
	Msg    string
	Sender *Player
}

type Game struct {
	players []*Player
	Queue   chan *Command // Incoming commands go here
	Quit    chan bool     // Send anything to this channel to end the game event loop
	Running bool          // Game event loop is running
	Started bool          // True if the game has begun, false if still in lobby
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

func (game *Game) AllReady() bool {
	for _, p := range game.players {
		if !p.IsReady {
			return false
		}
	}
	return true
}

// Communication

func (game *Game) Broadcast(msg string) {
	for _, p := range game.players {
		go p.Send(msg)
	}
}

func (game *Game) SendSpyStatus() {
	for _, p := range game.players {
		if p.IsSpy {
			go p.Send("spy")
		} else {
			go p.Send("resistance")
		}
	}
}

// Game states

func (game *Game) LobbyDone() bool {
	n := game.PlayerCount()
	return game.AllReady() && n >= MinPlayers && n <= MaxPlayers
}

// Event loop

func (game *Game) Stop() {
	game.Quit <- true
}

func (game *Game) HandleCommand(c *Command) {
	switch c.Msg {
	case "toggle_ready":
		c.Sender.ToggleReady()
		if game.LobbyDone() {
			game.Queue <- &Command{"start_game", nil}
		}

	case "start_game":
		game.Started = true
		game.ChooseSpies()
		game.SendSpyStatus()
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
