import game

class gamedict(object):
  def __init__(self):
    self.games = {}

  def game(self, instance):
    if instance not in self.games:
      self.games[instance] = game.game(instance)
    return self.games[instance]
