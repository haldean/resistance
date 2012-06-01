from tornado import web, ioloop
from sockjs.tornado import SockJSRouter, SockJSConnection
import gamedict
import userdict

games = gamedict.gamedict()
users = userdict.userdict()

class EchoConnection(SockJSConnection):
  def on_message(self, msg):
    print 'receive', msg
    cmd, args = msg.split(' ', 1)

    if cmd == 'CONNECT':
      instance, as_kw, username = args.split(' ')
      user = users.user(username, self)
      game = games.game(instance).connect(user)

    if cmd == 'READY':
      username = args
      user = users.user(username, self)
      user.setready(True)

    if cmd == 'NOTREADY':
      username = args
      user = users.user(username, self)
      user.setready(False)

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
