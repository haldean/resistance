import user

class userdict(object):
  def __init__(self):
    self.users = {}

  def user(self, username, connection):
    if username not in self.users:
      self.users[username] = user.user(username, connection)
    else:
      self.users[username].connection = connection
    return self.users[username]
