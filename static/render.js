// Generated by CoffeeScript 1.7.1
(function() {
  var escape;

  this.update = function(info) {
    var key, len, map, stat, statLengths, stats, uname, unameLength, _i, _len, _ref, _ref1, _ref2, _ref3;
    unameLength = "Username".length;
    statLengths = {};
    _ref = info["scores"][window.uname];
    for (key in _ref) {
      stat = _ref[key];
      statLengths[key] = key.length;
    }
    _ref1 = info["scores"];
    for (uname in _ref1) {
      stats = _ref1[uname];
      if (uname.length > unameLength) {
        unameLength = uname.length;
      }
      for (key in stats) {
        stat = stats[key];
        stat = String(stat);
        if (!(key in statLengths) || stat.length > statLengths[key]) {
          statLengths[key] = stat.length;
        }
      }
    }
    map = pad("Username", unameLength) + "|" + ((function() {
      var _results;
      _results = [];
      for (key in statLengths) {
        len = statLengths[key];
        _results.push(pad(key, len));
      }
      return _results;
    })()).join("|");
    map += "\n" + Array(map.length + 1).join("-");
    _ref2 = info["scores"];
    for (uname in _ref2) {
      stats = _ref2[uname];
      uname = pad(uname, unameLength);
      stats = ((function() {
        var _results;
        _results = [];
        for (key in statLengths) {
          len = statLengths[key];
          _results.push(pad(stats[key], len));
        }
        return _results;
      })()).join("|");
      console.log(uname.length);
      console.log(pad("Username", unameLength).length);
      map += "\n" + uname + "|" + stats;
    }
    document.getElementById("scores").innerHTML = escape(map);
    _ref3 = ["health", "ammo", "msg", "arena"];
    for (_i = 0, _len = _ref3.length; _i < _len; _i++) {
      key = _ref3[_i];
      if (key in info) {
        document.getElementById(key).innerHTML = escape(info[key]);
      }
    }
    return null;
  };

  this.pad = function(str, len) {
    str = String(str);
    str += Array(len - str.length + 1).join(" ");
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

}).call(this);
