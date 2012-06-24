class user(object):
  def __init__(self, username, connection):
    self.game = None
    self.name = username
    self.connection = connection
    self.ready = False
    self.vote = None
    self.spy = None

  def setready(self, isready):
    if isready:
      self.game.ready(self)
    else:
      self.game.notready(self)
