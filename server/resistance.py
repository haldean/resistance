from tornado import web, ioloop
from sockjs.tornado import SockJSRouter, SockJSConnection
import gamedict
import userdict

games = gamedict.gamedict()
users = userdict.userdict()

class EchoConnection(SockJSConnection):
  def on_message(self, msg):
    print 'receive', msg
    if ' ' in msg:
      cmd, args = msg.split(' ', 1)
    else:
      cmd = msg
    cmd = cmd.lower()

    if cmd == 'connect':
      username, instance = args.split(' ')
      self.user = users.user(username, self)
      self.game = games.game(instance)
      self.user.game = self.game
      self.game.connect(self.user)

    elif cmd == 'ready':
      self.user.setready(True)

    elif cmd == 'notready':
      self.user.setready(False)

    elif cmd == 'help':
      self.game.send_help(self.user)

    elif cmd == 'connected':
      self.game.send_connected(self.user)

    elif cmd == 'leader':
      self.game.send_leader(self.user)

    elif cmd == 'choose':
      self.game.choose_team(self.user, args.split(' '))

    elif cmd == 'pass':
      self.game.vote(self.user, True)

    elif cmd == 'fail':
      self.game.vote(self.user, False)

    elif cmd == 'affiliation':
      self.game.send_affiliation(self.user)

    elif cmd == 'missions':
      self.game.send_missions(self.user)

    else:
      self.user.connection.send('Unknown command "%s"' % cmd)

  def on_close(self):
    self.game.disconnect(self.user)

def main(args):
  port = args and int(args[0]) or 8001
  router = SockJSRouter(EchoConnection, '/echo')
  app = web.Application(router.urls)
  app.listen(port)

  print 'Server listening at localhost:%d' % (port,)
  ioloop.IOLoop.instance().start()

if __name__ == '__main__':
  import sys
  main(sys.argv[1:])
