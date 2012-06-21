(function(){
  if (window.location.hash == '#dead') return;

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
      $('#error-popup-content').text(_.rest(msg_parts).join(' '));
      $('#error-popover').css('display', 'block');
    } else if (msg_parts[0] == 'CONNECTED') {
      connected = true;
      $('#users').html('');
      _.each(_.rest(msg_parts), function(username) {
        $('#users').append('<li class="user ' + username + '">'
          + username + '</li>');
      });

    } else if (msg_parts[0] == 'READY') {
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

    } else if (msg_parts[0] == 'SIZES') {
      $('#lobby').css('display', 'none');
      ready_button.css('display', 'none');
      $('#game').css('display', 'block');
      for (var i = 0; i < 5; i++) {
        $('#round' + i).text('(' + msg_parts[i+1] + ')');
      }

    } else if (msg_parts[0] == 'SPY') {
      $('#msg-popup-content').html(
          'You have been identified as a spy.<br>' +
          'Please identify all other spies.');
      $('#msg-popover').css('display', 'block');
      $('#msg-popup-dismiss').text('Spies have been identified');
      $('.icon').css('display', 'none');
      $('.spy-icon').css('display', 'block');

    } else if (msg_parts[0] == 'RESISTANCE') {
      $('#msg-popup-content').html(
          'You have been identified as a resistance member.<br>' +
          'Please allow spies to identify each other.');
      $('#msg-popover').css('display', 'block');
      $('#msg-popup-dismiss').text('Ready');
      $('.icon').css('display', 'none');
      $('.resistance-icon').css('display', 'block');

    } else if (msg_parts[0] == 'LEADER') {
      if (msg_parts[1] == username) {
        $('#leader').css('display', 'block');
        $('#rounds').addClass('fade');
        $('#leader-pick').html('');
        _.each(_.rest(msg_parts, 3), function(username) {
          $('#leader-pick').append(make_leader_pick_user(username));
        });
        $('#leader-pick').append(make_propose_team());
      } else {
        $('#leader').css('display', 'none');
        $('#rounds').removeClass('fade');
        $('#msg-popup-content').html(
            msg_parts[1] + ' has been selected as the first team leader.');
        $('#msg-popover .popup img').attr('src', 'img/leader.png');
        $('#msg-popover').css('display', 'block');
        $('#msg-popup-dismiss').text('Dismiss');
      }
    }
  }

  var make_leader_pick_user = function(username) {
    var pick = $.create('li').addClass(user).addClass(username);
    pick.html('<i class="icon-remove"></i>' + username);
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

    $('#msg-popup-dismiss').click(function(e) {
      e.preventDefault();
      e.stopPropagation();
      $('#msg-popover').css('display', 'none');
      send('READY ' + username);
    });
  }

  $.domReady(function() {
    ready_button = $('#ready');
    setup_event_handlers();

    $('.username').text(username);
  });
})();
