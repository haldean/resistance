package resistance

import (
	"testing"
	"time"
)

func TestStartStop(t *testing.T) {
	g := NewGame()

	go g.Loop()
	time.Sleep(100)
	if !g.Running {
		t.Error("Game.Loop should start the game running.")
	}

	g.Quit <- true
	time.Sleep(100)
	if g.Running {
		t.Error("Sending quit command should stop the game.")
	}
}

func TestHandleCommand(t *testing.T) {
	g := NewGame()
	p := NewTestPlayer("test")
	g.AddPlayer(p)

	g.HandleCommand(&Command{Msg: "toggle_ready", Sender: p})
	if !p.IsReady {
		t.Error("Sending toggle_ready command should set player to ready")
	}

	g.HandleCommand(&Command{Msg: "toggle_ready", Sender: p})
	if p.IsReady {
		t.Error("Sending toggle_ready command twice should set player to not ready")
	}
}

func CheckChooseSpies(t *testing.T, players int, expectSpies int) {
	g := NewGame()
	for i := 0; i < players; i++ {
		g.AddPlayer(NewTestPlayer("test"))
	}

	g.ChooseSpies()

	spies := 0
	for _, p := range g.players {
		if p.IsSpy {
			spies++
		}
	}
	if spies != expectSpies {
		t.Errorf("A %d-person game should have %d spies.", players, expectSpies)
	}
}

func TestChooseSpies(t *testing.T) {
	CheckChooseSpies(t, 4, 0)
	CheckChooseSpies(t, 5, 2)
	CheckChooseSpies(t, 6, 2)
	CheckChooseSpies(t, 7, 3)
	CheckChooseSpies(t, 8, 3)
	CheckChooseSpies(t, 9, 3)
	CheckChooseSpies(t, 10, 4)
	CheckChooseSpies(t, 11, 0)
}

func TestSendSpyStatus(t *testing.T) {
	g := NewGame()
	for i := 0; i < 5; i++ {
		g.AddPlayer(NewTestPlayer("test"))
	}
	g.ChooseSpies()
	g.SendSpyStatus()

	// Wait for messages to be sent
	time.Sleep(100)

	spies := 0
	for _, p := range g.players {
		switch {
		case p.LastMessage == "spy":
			spies++
		case p.LastMessage != "resistance":
			t.Errorf("Player should be sent SPY or RESISTANCE, but was sent %s",
				p.LastMessage)
		}
	}
}

func TestLobby(t *testing.T) {
	g := NewGame()
  go g.Loop()
  defer g.Stop()

  if g.Started {
    t.Error("Game should start in lobby mode.")
  }

	for i := 0; i < 7; i++ {
		g.AddPlayer(NewTestPlayer("test"))
	}

	if g.AllReady() {
		t.Error("Players should start not ready.")
	}

	for i := 0; i < 6; i++ {
    g.Queue <- &Command{ Msg: "toggle_ready", Sender: g.players[i]}
    time.Sleep(50)
    if !g.players[i].IsReady {
      t.Error("Sending ready message should set player to ready.")
    } else if g.AllReady() {
			t.Error("AllReady should return false if not all players are ready.")
		}
	}

  if g.Started {
    t.Error("Game should not start unless all players are ready.")
  }

  g.Queue <- &Command{ Msg: "toggle_ready", Sender: g.players[6]}
  time.Sleep(50)
	if !g.AllReady() {
		t.Error("AllReady should return true if all players are ready.")
	}

  if !g.Started {
    t.Error("Game should start when all players are ready.")
  }
}

func TestBadPlayerCount(t *testing.T) {
  g := NewGame()
  go g.Loop()
  defer g.Stop()

  for i := 0; i < 4; i++ {
    p := NewTestPlayer("test")
    g.AddPlayer(p)
    g.Queue <- &Command{ Msg: "toggle_ready", Sender: p}
  }

  if g.Started {
    t.Error("Game should not start with too few players.")
  }

  for i := 0; i < 4; i++ {
    g.Queue <- &Command{ Msg: "toggle_ready", Sender: g.players[i] }
  }

  for i := 0; i < 20; i++ {
    g.AddPlayer(NewTestPlayer("test"))
  }

  for i := 0; i < len(g.players); i++ {
    g.Queue <- &Command{ Msg: "toggle_ready", Sender: g.players[i] }
    time.Sleep(50)

    if g.Started {
      t.Error("Game should not start with too many players.")
    }
  }

  if !g.AllReady() {
    t.Error("Your test is bad and you should feel bad.")
  }
}
