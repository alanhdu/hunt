// Generated by CoffeeScript 1.7.1
(function() {
  var displayArena, escape, formatNumber, getScoreboard, getType, pad;

  $("#square").on("click", (function() {
    if ($("#square").prop("checked")) {
      return $(".rect").removeClass("rect").addClass("square");
    } else {
      return $(".square").removeClass("square").addClass("rect");
    }
  }));

  this.update = function(info) {
    var key, _i, _j, _len, _len1, _ref, _ref1;
    document.getElementById("scores").innerHTML = getScoreboard(info["scores"]);
    document.getElementById("arena").innerHTML = displayArena(info["arena"], info["x"], info["y"]);
    _ref = ["msg", "cloak", "scan"];
    for (_i = 0, _len = _ref.length; _i < _len; _i++) {
      key = _ref[_i];
      if (key in info) {
        document.getElementById(key).innerHTML = escape(info[key]);
      }
    }
    _ref1 = ["health", "ammo"];
    for (_j = 0, _len1 = _ref1.length; _j < _len1; _j++) {
      key = _ref1[_j];
      document.getElementById(key).innerHTML = formatNumber(info[key]);
    }
    return null;
  };

  this.clear = function() {
    var key, _i, _len, _ref, _results;
    _ref = ["health", "ammo", "msg", "arena", "scores", "cloak", "scan"];
    _results = [];
    for (_i = 0, _len = _ref.length; _i < _len; _i++) {
      key = _ref[_i];
      _results.push(document.getElementById(key).innerHTML = "");
    }
    return _results;
  };

  displayArena = function(arena, curX, curY) {
    var char, s, str, x, y, _i, _len;
    x = 0;
    y = 0;
    str = "";
    for (_i = 0, _len = arena.length; _i < _len; _i++) {
      char = arena[_i];
      s = getType(char, arena, x, y);
      if (x === curX && y === curY) {
        str += "<span id='highlight'>" + s + "</span id='highlight'>";
      } else {
        str += s;
      }
      if (char === '\n') {
        y += 1;
        x = 0;
      } else {
        x += 1;
      }
    }
    return str;
  };

  getType = function(char, arena, x, y) {
    var bot, height, left, pos, right, top, type, visible, width;
    if (char !== "#" && char !== "*") {
      return escape(char);
    }
    height = (arena.split("\n").length);
    width = (arena.length - height + 1) / height;
    pos = y * (width + 1) + x;
    top = pos - width - 1;
    bot = pos + width + 1;
    left = pos - 1;
    right = pos + 1;
    if (char === '*') {
      type = 0;
      if (arena[left] === '*' || arena[right] === '*') {
        type += 1;
      }
      if (arena[top] === '*' || arena[bot] === '*') {
        type += 2;
      }
      return ((function() {
        switch (type) {
          case 0:
            return '+';
          case 1:
            return '-';
          case 2:
            return '|';
          case 3:
            return '+';
        }
      })());
    } else if (char === '#') {
      visible = function(x) {
        return x === '#' || x === '#';
      };
      if (visible(arena[left])) {
        if (visible(arena[right])) {
          if (visible(arena[top]) && visible(arena[bot])) {
            return '*';
          } else {
            return '|';
          }
        } else {
          if (visible(arena[top])) {
            if (visible(arena[bot])) {
              return '-';
            } else {
              return '\\';
            }
          } else {
            return '/';
          }
        }
      } else {
        if (visible(arena[top])) {
          if (visible(arena[bot])) {
            return '-';
          } else {
            return '/';
          }
        } else {
          return '\\';
        }
      }
    }
  };

  getScoreboard = function(scores) {
    var key, len, map, stat, statLengths, stats, uname, unameLength, xp, _ref;
    unameLength = "Username".length;
    statLengths = {};
    _ref = scores[window.uname];
    for (key in _ref) {
      stat = _ref[key];
      statLengths[key] = key.length;
    }
    for (uname in scores) {
      stats = scores[uname];
      if (uname.length > unameLength) {
        unameLength = uname.length;
      }
      for (key in stats) {
        stat = stats[key];
        stat = formatNumber(stat);
        if (!(key in statLengths) || stat.length > statLengths[key]) {
          statLengths[key] = stat.length;
        }
      }
    }
    xp = 2;
    map = pad("Username", unameLength + xp) + "|" + ((function() {
      var _results;
      _results = [];
      for (key in statLengths) {
        len = statLengths[key];
        _results.push(pad(key, len + xp));
      }
      return _results;
    })()).join("|");
    map += "\n" + Array(map.length + 1).join("-");
    for (uname in scores) {
      stats = scores[uname];
      uname = pad(uname, unameLength + xp);
      stats = ((function() {
        var _results;
        _results = [];
        for (key in statLengths) {
          len = statLengths[key];
          _results.push(pad(formatNumber(stats[key]), len + xp));
        }
        return _results;
      })()).join("|");
      map += "\n" + uname + "|" + stats;
    }
    return escape(map);
  };

  pad = function(str, len) {
    var left, right;
    str = String(str);
    left = Math.floor((len - str.length) / 2) + 1;
    right = Math.ceil((len - str.length) / 2) + 1;
    str = Array(left).join(" ") + str + Array(right).join(" ");
    return str;
  };

  escape = function(str) {
    return String(str).replace(/[& <>"\n]/g, function(chr) {
      switch (chr) {
        case '\n':
          return "<br/>";
        case ' ':
          return "&nbsp;";
        case '>':
          return "&gt;";
        case '<':
          return "&lt;";
        case '"':
          return "&quot;";
        case '&':
          return "&amp;";
      }
    });
  };

  formatNumber = function(num) {
    return Number(num).toFixed(2);
  };

}).call(this);
