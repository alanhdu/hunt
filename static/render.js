// Generated by CoffeeScript 1.7.1
this.render = function(arena) {
  var chr, i, map, _i, _len;
  map = "";
  for (i = _i = 0, _len = arena.length; _i < _len; i = ++_i) {
    chr = arena[i];
    switch (chr) {
      case '\n':
        map += "<br />";
        break;
      case ' ':
        map += "&nbsp;";
        break;
      case '>':
        map += "&gt;";
        break;
      case '<':
        map += "&lt;";
        break;
      default:
        map += chr;
    }
  }
  return (document.getElementById("map")).innerHTML = map;
};
