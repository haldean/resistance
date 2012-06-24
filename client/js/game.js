(function(){
  if (window.location.hash == '#dead') return;

  var _ = require('underscore');

  var connected = false;
  var term;

  function send(msg) {
    sock.send(msg);
    console.log('< ' + msg);
  }

  function write(msg) {
    if (msg[0] == "/") {
      term.clear();
      msg = msg.substring(1);
    }
    if (msg[0] == "!") {
      msg = msg.substring(1);
      term.write('%c(red)' + msg + '%c(default)');
    } else {
      term.write('%c(green)' + msg + '%c(default)');
    }
  }

  var sock = new SockJS('http://localhost:8001/echo');
  sock.onopen = function() {
    write('Please use the connect command to connect to an instance' +
      '\nExample: connect [username] [instance name]' +
      '\nIf the instance name does not exist, it will be created\n');
  }

  sock.onclose = function() {
    console.log('disconnected');
    term.write('%c(red)You have been disconnected from the instance');
  }

  sock.onmessage = function(msg) {
    console.log('> ' + msg.data);
    write(msg.data);
    term.prompt();
  }

  $.domReady(function() {
    term = new Terminal({
      handler: function() {
        this.newLine();
        var line = this.lineBuffer;
        send(line);
        this.prompt();
      },
      ps: '',
      greeting: '%c(green)Connecting to resistance network...%c(default)',
      bgColor: 'none',
      frameColor: 'none'
    });
    //term.cursorOn();
    term.open();
  });
})();
