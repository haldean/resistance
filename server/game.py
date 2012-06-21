from enum import enum
import random
import rules

# Game states
game_states = enum(
    'LOBBY',
    'PICK_SPIES',
    'PICK_FIRST_LEADER',
    'PICK_LEADER',
    'WAIT_FOR_TEAM',
    'VOTE_ON_TEAM',
    'TEAM_VOTE_FAILED',
    'ON_MISSION',
    'ANNOUNCE_RESULTS',
    'RESISTANCE_WIN',
    'SPIES_WIN',
    )()

class game(object):
  min_users = 5
  max_users = 10

  def __init__(self, name):
    self.name = name
    self.users = []
    self.state = game_states.LOBBY
    self.leader = 0
    self.mission = 0

  def transition(self, new_state):
    print 'Now in state', new_state
    if new_state == game_states.PICK_SPIES:
      self.broadcast('SIZES %s' %
          ' '.join(str(x) for x in rules.mission_sizes(len(self.users))))
      self.pick_spies()
    elif new_state == game_states.PICK_FIRST_LEADER:
      self.leader = random.randint(0, len(self.users) - 1)
      self.transition(game_states.PICK_LEADER)
    elif new_state == game_states.PICK_LEADER:
      self.leader += 1
      self.leader %= len(self.users)
      self.broadcast('LEADER %s %d %s' % (
        self.users[self.leader].name,
        rules.mission_size(len(self.users), self.mission),
        ' '.join(user.name for user in self.users)
        ))
    self.state = new_state

  def broadcast(self, msg):
    self.users[0].connection.broadcast(
        map(lambda x: x.connection, self.users), msg)

  def connect(self, user):
    if self.state == game_states.LOBBY:
      if user.name not in map(lambda x: x.name, self.users):
        self.users.append(user)
        user.game = self
      self.broadcast_connected()
      self.broadcast_ready()
    else:
      user.connection.send('ERROR This game is locked for play.')

  def disconnect(self, user):
    self.users.remove(user)
    if self.state == game_states.LOBBY:
      self.broadcast_connected()
      self.broadcast_ready()

  def ready(self, user):
    user.ready = True
    if self.state == game_states.LOBBY:
      self.broadcast_ready()

    if self.all_ready():
      if self.state == game_states.LOBBY:
        self.transition(game_states.PICK_SPIES)
      elif self.state == game_states.PICK_SPIES:
        self.transition(game_states.PICK_FIRST_LEADER)

  def notready(self, user):
    user.ready = False
    self.broadcast_ready()

  def pick_spies(self):
    self.broadcast('ALLREADY')
    spies = rules.spies_for_team([x.name for x in self.users])
    for user in self.users:
      user.ready = False
      if user.name in spies:
        user.connection.send('SPY')
      else:
        user.connection.send('RESISTANCE')

  def all_ready(self):
    return all(map(lambda x: x.ready, self.users)) and \
        self.min_users <= len(self.users) <= self.max_users

  def broadcast_connected(self):
    self.broadcast('CONNECTED %s' %
        ' '.join(map(lambda x: x.name, self.users)))

  def broadcast_ready(self):
    self.broadcast('READY %s' % ' '.join(x.name for x in self.users if x.ready))
