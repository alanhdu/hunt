// Generated by CoffeeScript 1.7.1
var socket;

socket = io.connect();

socket.on("update", render);

$("#play").on("click", (function() {
  window.username = $("#username").val();
  return socket.emit('begin', {
    width: 51,
    height: 23,
    username: username
  });
}));

$(window).keydown((function(evt) {
  var chr, direction, key, type, username;
  if (evt.target.tagName.toLowerCase() === "input") {
    return true;
  }
  key = evt.which;
  chr = String.fromCharCode(key);
  evt.preventDefault();
  if (evt.shiftKey) {
    type = "turn";
  } else {
    type = "move";
  }
  switch (chr) {
    case 'J':
      direction = 'v';
      break;
    case 'K':
      direction = '^';
      break;
    case 'L':
      direction = '>';
      break;
    case 'H':
      direction = '<';
  }
  if (direction !== void 0) {
    username = window.username;
    return socket.emit(type, {
      direction: direction,
      username: username
    });
  }
}));