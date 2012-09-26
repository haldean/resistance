package resistance

import (
  "math/rand"
)

var MinPlayers int = 5
var MaxPlayers int = 10

var SpyCount map[int] int = map[int] int {
  5: 2,
  6: 2,
  7: 3,
  8: 3,
  9: 3,
  10: 4,
}

var MissionSize map[int] [5]int = map[int] [5]int {
  5: [5]int{ 2, 3, 2, 3, 3 },
  6: [5]int{ 2, 3, 4, 3, 4 },
  7: [5]int{ 2, 3, 3, 4, 4 },
  8: [5]int{ 3, 4, 4, 5, 5 },
  9: [5]int{ 3, 4, 4, 5, 5 },
  10: [5]int{ 3, 4, 4, 5, 5 },
}

// Returns true if the number of players in the game is valid for the game to
// begin (i.e., between 5 and 10 inclusive).
func (game *Game) GoodPlayerCount() bool {
  return 5 <= game.PlayerCount() && game.PlayerCount() <= 10
}

// Randomly chooses the necessary amount of spies by setting the Player.IsSpy
// value on all players in the game.
func (game *Game) ChooseSpies() {
  for _, p := range game.players {
    p.IsSpy = false
  }

  if !game.GoodPlayerCount() {
    return
  }

  needed := SpyCount[game.PlayerCount()]
  for needed > 0 {
    idx := rand.Int() % game.PlayerCount()
    if !game.players[idx].IsSpy {
      game.players[idx].IsSpy = true
      needed--
    }
  }
}
