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

  g.HandleCommand(&Command{Msg: "toggleready", Sender:p})
  if !p.IsReady {
    t.Error("Sending toggleready command should set player to ready")
  }

  g.HandleCommand(&Command{Msg: "toggleready", Sender:p})
  if p.IsReady {
    t.Error("Sending toggleready command twice should set player to not ready")
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

func TestAllReady(t *testing.T) {
  g := NewGame()
  for i := 0; i < 7; i++ {
    g.AddPlayer(NewTestPlayer("test"))
  }

  if g.AllReady() {
    t.Error("Players should start not ready")
  }

  for i := 0; i < 6; i++ {
    g.players[i].IsReady = true
    if g.AllReady() {
      t.Error("AllReady should return false if not all players are ready")
    }
  }

  g.players[6].IsReady = true
  if !g.AllReady() {
    t.Error("AllReady should return true if all players are ready")
  }
}
