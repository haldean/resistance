(function(){
  var _ = require('underscore');
  var sock = new SockJS('http://localhost:8001/echo');

  var ingame = false;
  var connected = false;

  var uri = URI.parseQuery(window.location.search);
  var instance = uri.server;
  var username = uri.username;

  var ready_button;

  if (! username.match(/^[a-zA-Z_.\-0-9]+$/)) {
    window.location = 'index.html#badusername';
  } else if (! instance.match(/^[a-zA-Z_.\-0-9]+$/)) {
    window.location = 'index.html#badserver';
  }

  function send(msg) {
    sock.send(msg);
    console.log('send: ' + msg);
  }

  sock.onopen = function() {
    send('CONNECT ' + instance + ' AS ' + username);
  }

  sock.onclose = function() {
    console.log('closed');
  }

  sock.onmessage = function(msg) {
    console.log('receive: ' + msg.data);

    var msg_parts = msg.data.trim().split(' ');

    if (msg_parts[0] == 'ERROR') {
      connected = false;
      $('#popup-content').text(_.rest(msg_parts).join(' '));
      $('#popover').css('display', 'block');
    } else if (! connected && msg_parts[0] == 'CONNECTED') {
      connected = true;
      $('#users').html('');
      _.each(_.rest(msg_parts), function(username) {
        $('#users').append('<li class="user ' + username + '">'
          + username + '</li>');
      });

    } else if (connected && msg_parts[0] == 'READY') {
      $('.user').each(function(e) {
        $(e).removeClass('readyuser');
      });

      if (msg_parts.length == 1) {
        return;
      }

      _.each(_.rest(msg_parts), function(ready_user) {
        $('.' + ready_user).addClass('readyuser');
      });

      if (_.indexOf(msg_parts, username) >= 0) {
        ready_button.removeClass('notready');
        ready_button.addClass('ready');
      } else {
        ready_button.addClass('notready');
        ready_button.removeClass('ready');
      }
    }
  }

  var setup_event_handlers = function() {
    ready_button.click(function(e) {
      if (ready_button.hasClass('ready')) {
        ready_button.removeClass('ready');
        ready_button.addClass('notready');
        send('NOTREADY ' + username);
      } else {
        ready_button.removeClass('notready');
        ready_button.addClass('ready');
        send('READY ' + username);
      }
    });

    $('#reload-page-link').click(function(e) {
      e.preventDefault();
      e.stopPropagation();
      window.location.reload();
    });
  }

  $.domReady(function() {
    ready_button = $('#ready');
    setup_event_handlers();
  });
})();
