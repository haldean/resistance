import random
import rules

from pytomaton import *

class game(statemachine):
  min_users = 5
  max_users = 10

  start_state = 'lobby'
  states = [
      'lobby',
      'pick_spies',
      'identify_spies',
      'pick_first_leader',
      'pick_leader',
      'wait_for_team',
      'vote_on_team',
      'on_mission',
      'resistance_win',
      'spies_win',
      'game_over',
      ]

  def __init__(self, name):
    statemachine.__init__(self)
    self.name = name
    self.users = []
    self.leader = None
    self.mission = 0
    self.failed_votes = 0
    self.missions = [None] * 5

  def transition(self, to_state):
    print 'transitioning to state %s' % to_state
    statemachine.transition(self, to_state)
    print 'in state %s' % self._current_state

  def broadcast(self, msg):
    self.users[0].connection.broadcast(
        map(lambda x: x.connection, self.users), msg)

  def connect(self, user):
    if user not in self.users:
      self.users.append(user)
    user.ready = False
    user.send('Connected. Welcome to the instance.\n\n' +
        'Type commands using the keyboard, and hit enter to send ' +
        'to the central server\n' +
        'Type "help" to see a list of commands\n\n' +
        'Send ready command when all players have joined.')
    self.send_connected(user)

  def disconnect(self, user):
    self.users.remove(user)
    self.broadcast('%s has disconnected' % user.name)

  @on_enter('pick_first_leader')
  def pick_first_leader(self):
    self.leader = random.randint(0, len(self.users) - 1)
    self.transition('pick_leader')

  @on_enter('pick_leader')
  def pick_leader(self):
    self.leader += 1
    self.leader = self.leader % len(self.users)
    self.broadcast(self.users[self.leader].name + ' is now Team Leader')
    self.transition('wait_for_team')

  @on_enter('wait_for_team')
  def ask_for_team(self):
    leader_user = self.users[self.leader]
    leader_user.send(('Use the "choose" command to send %d ' +
        'usernames (space-separated) for mission\n') %
        rules.mission_size(len(self.users), self.mission))

  def on_ready_change(self):
    print self._current_state
    if self.all_ready():
      if self.in_state('lobby'):
        self.transition('pick_spies')
      elif self.in_state('identify_spies'):
        self.transition('pick_first_leader')

  def ready(self, user):
    user.ready = True
    user.send('Ready status confirmed.')
    self.send_connected(user)
    self.on_ready_change()

  def notready(self, user):
    user.ready = False
    user.send('Ready status withdrawn.')
    self.send_connected(user)
    self.on_ready_change()

  @on_enter('pick_spies')
  def pick_spies(self):
    self.broadcast('/All users are ready. Determining affiliations...')
    spies = rules.spies_for_team([x.name for x in self.users])
    for user in self.users:
      user.ready = False
      if user.name in spies:
        user.spy = True
        user.send('You are a spy! Please identify the other spies.\n'
            + 'Send "READY" when you\'re done.')
      else:
        user.spy = False
        user.send('You are a rebel! Please allow the '
            + 'spies to identify each other.\nSend "READY" when they\'re done.')
    for user in self.users:
      if user.spy:
        user.send('Other spies: ' + ', '.join([user.name for user in self.users if user.spy])
    self.transition('identify_spies')

  def choose_team(self, proposing_user, proposed_team):
    proposed_team = set(proposed_team)

    if proposing_user != self.users[self.leader]:
      proposing_user.send('You are not team leader.')
      return

    required_users = rules.mission_size(len(self.users), self.mission)
    if len(proposed_team) != required_users:
      proposing_user.send(('You must pick a team of %d users ' +
        '(received a team of %d)') % (required_users, len(proposed_team)))
      return

    possible_usernames = set([user.name for user in self.users])
    if not proposed_team <= possible_usernames:
      proposing_user.send('Invalid usernames: %s' %
          ', '.join(proposed_team - possible_usernames))
      return

    self.proposed_team = []
    for user in self.users:
      if user.name in proposed_team:
        self.proposed_team.append(user)
    self.transition('vote_on_team')

  @on_enter('vote_on_team')
  def vote_on_team(self):
    for user in self.users:
      user.vote = None
    self.broadcast('The following team has been proposed:')
    self.broadcast(', '.join(user.name for user in self.proposed_team))
    self.broadcast('Vote for or against this team using the pass or fail command')

  def vote_count(self, users):
    if all(user.vote != None for user in users):
      yes_votes = len([user for user in users if user.vote])
      no_votes = len(users) - yes_votes
      return (yes_votes, no_votes)
    return None

  def check_team_votes(self):
    vote_count = self.vote_count(self.users)
    if vote_count != None:
      yes_votes, no_votes = vote_count
      self.broadcast('Final vote: %d pass, %d fail' % (yes_votes, no_votes))

      if yes_votes > no_votes:
        self.broadcast('Vote passes')
        self.transition('on_mission')
        self.failed_votes = 0
      else:
        self.broadcast('Vote fails')
        self.transition('pick_leader')
        self.failed_votes += 1
        if self.failed_votes >= 3:
          self.transition('spies_win')

  def check_mission_votes(self):
    vote_count = self.vote_count(self.proposed_team)
    if vote_count != None:
      yes_votes, no_votes = vote_count
      self.broadcast('Final vote: %d pass, %d fail' % (yes_votes, no_votes))

      if no_votes == 0:
        self.broadcast('!Mission is successful')
        self.missions[self.mission] = (True, self.proposed_team)
      else:
        self.broadcast('!Mission has failed')
        self.missions[self.mission] = (False, self.proposed_team)
      self.mission += 1
      self.check_if_won()
      self.transition('pick_leader')

  def check_if_won(self):
    passes, fails = 0, 0
    for mission_passed, team in self.missions[:self.mission]:
      if mission_passed:
        passes += 1
      else:
        fails += 1
    if passes == 3:
      self.transition('resistance_win')
    elif fails == 3:
      self.transition('spies_win')

  @on_enter('on_mission')
  def on_mission(self):
    self.broadcast('!The mission has begun')
    for user in self.proposed_team:
      user.vote = None
      user.send('You are on the mission.\nUse the pass or fail commands.')

  @on_enter('resistance_win')
  def resistance_win(self):
    self.broadcast('!The rebels have won.\nSpies: %s' %
        ', '.join(user.name for user in self.users if user.spy))
    self.transition('game_over')

  @on_enter('spies_win')
  def spies_win(self):
    self.broadcast('!The spies have won.\nSpies: %s' %
        ', '.join(user.name for user in self.users if user.spy))
    self.transition('game_over')

  @on_enter('game_over')
  def game_over(self):
    for user in self.users:
      user.connection.disconnect()

  def vote(self, user, passes):
    if not (self.in_state('vote_on_team') or self.in_state('on_mission')):
      user.send('Cannot vote at this time')
      return
    user.vote = passes
    if passes:
      user.send('Pass vote received')
    else:
      user.send('Fail vote received')
    if self.in_state('vote_on_team'):
      self.check_team_votes()
    else:
      self.check_mission_votes()

  def all_ready(self):
    return all(map(lambda x: x.ready, self.users)) and \
        self.min_users <= len(self.users) <= self.max_users

  def send_connected(self, user):
    def print_user(user):
      if user.ready:
        return '%s (*)' % user.name
      else:
        return user.name
    user.send('Connected users: %s' %
        ', '.join(map(print_user, self.users)))

  def send_leader(self, user):
    if self.leader != None:
      user.send('%s is team leader.' % self.users[self.leader].name)
    else:
      user.send('There is currently no team leader')

  def send_affiliation(self, user):
    if user.spy:
      user.send('You are a spy')
    else:
      user.send('You are a rebel')

  def send_missions(self, user):
    def format_round_info(round_info):
      i, round_info = round_info
      if round_info != None:
        success, members = round_info
        if success:
          return 'Passed     %s' % ' '.join(user.name for user in members)
        else:
          return 'Failed     %s' % ' '.join(user.name for user in members)
      else:
        return 'Not played (%d users)' % rules.mission_size(len(self.users), i)
    user.send('\n'.join(map(format_round_info, enumerate(self.missions))))

  def send_help(self, user):
    user.send('''Available commands:
    help:         Displays this information
    connected:    Displays connected users
    affiliation:  Displays your affiliation
    missions:     Displays round information
    leader:       Displays the team leader's username
    choose:       Chooses a list of users when you are team leader
    ready:        Announces ready status
    notready:     Withdraw ready status
    pass:         Vote for passing a motion or mission
    fail:         Vote to fail a motion or mission''')
