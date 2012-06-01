class game(object):
  def __init__(self, name):
    self.name = name
    self.users = []
    self.in_lobby = True

  def broadcast(self, msg):
    print 'broadcast', msg
    self.users[0].connection.broadcast(
        map(lambda x: x.connection, self.users), msg)

  def connect(self, user):
    if self.in_lobby:
      if user.name not in map(lambda x: x.name, self.users):
        self.users.append(user)
        user.game = self
      self.broadcast('CONNECTED %s' %
          ' '.join(map(lambda x: x.name, self.users)))
    else:
      user.connection.send('ERROR This game is locked for play.')
    self.broadcast_ready()

  def broadcast_ready(self):
    if all(map(lambda x: x.ready, self.users)):
      self.in_lobby = False
    else:
      self.in_lobby = True
    self.broadcast('READY %s' % 
        ' '.join(map(lambda x: x.name,
                     filter(lambda x: x.ready, self.users))))

  def ready(self, user):
    user.ready = True
    self.broadcast_ready()

  def notready(self, user):
    user.ready = False
    self.broadcast_ready()
