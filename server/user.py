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

  def send(self, msg):
    self.connection.send(msg)

  def command(self, msg):
    print 'receive', msg
    if ' ' in msg:
      cmd, args = msg.split(' ', 1)
    else:
      cmd = msg
    cmd = cmd.lower()

    if cmd == 'ready':
      self.setready(True)

    elif cmd == 'notready':
      self.setready(False)

    elif cmd == 'help':
      self.game.send_help(self)

    elif cmd == 'connected':
      self.game.send_connected(self)

    elif cmd == 'leader':
      self.game.send_leader(self)

    elif cmd == 'choose':
      self.game.choose_team(self, args.split(' '))

    elif cmd == 'pass':
      self.game.vote(self, True)

    elif cmd == 'fail':
      self.game.vote(self, False)

    elif cmd == 'affiliation':
      self.game.send_affiliation(self)

    elif cmd == 'missions':
      self.game.send_missions(self)

    else:
      self.send('Unknown command "%s"' % cmd)

