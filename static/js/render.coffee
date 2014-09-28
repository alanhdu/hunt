@update = (info) ->
    document.getElementById("scores").innerHTML = getScoreboard(info["scores"])
    document.getElementById("arena").innerHTML = displayArena(info["arena"], info["x"], info["y"])

    for key in ["health", "ammo", "msg"]
        if key of info
            document.getElementById(key).innerHTML = escape(info[key])

    null

@clear = () ->
    for key in ["health", "ammo", "msg", "arena", "scores"]
        document.getElementById(key).innerHTML = ""

displayArena = (arena, curX, curY) ->
    x = 0
    y = 0
    str = ""
    for char in arena
        s = switch char
                when '\n' then "<br/>"
                when ' ' then "&nbsp;"
                when '>' then "&gt;"
                when '<' then "&lt;"
                when '"' then "&quot;"
                when '&' then "&amp;"
                else char


        if x == curX and y == curY
            str += "<span id='highlight'>" + s + "</span id='highlight'>"
        else
            str += s

        if char == '\n'
            y += 1
            x = 0
        else
            x += 1

    return str



getScoreboard = (scores) ->
    unameLength = "Username".length
    statLengths = {}

    for key, stat of scores[window.uname]
        statLengths[key] = key.length
    for uname, stats of scores
        if uname.length > unameLength
            unameLength = uname.length
        for key, stat of stats
            stat = String(stat)
            if key not of statLengths or stat.length > statLengths[key]
                statLengths[key] = stat.length

    map = pad("Username", unameLength) + "|" + (pad(key, len) for key, len of statLengths).join("|")
    map += "\n" + Array(map.length + 1).join("-")

    for uname, stats of scores
        uname = pad(uname, unameLength)
        stats = (pad(stats[key], len) for key, len of statLengths).join("|")
        map += "\n#{uname}|#{stats}"

    return escape(map)

pad = (str, len) ->
    str = String(str)
    str += Array(len - str.length + 1).join(" ")
    return str

escape = (str) ->
    String(str).replace(/[& <>"\n]/g, (chr) ->
        switch chr
            when '\n' then "<br/>"
            when ' ' then "&nbsp;"
            when '>' then "&gt;"
            when '<' then "&lt;"
            when '"' then "&quot;"
            when '&' then "&amp;"
    )
