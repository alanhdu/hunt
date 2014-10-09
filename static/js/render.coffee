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
        s = getType(char, arena, x, y)

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

getType = (char, arena, x , y) ->
    if char isnt "#" and char isnt "*"
        return escape(char)

    height = (arena.split("\n").length)
    width = (arena.length - height + 1) / height
    pos = y * (width + 1) + x
    top = pos - width - 1
    bot = pos + width + 1
    left = pos - 1
    right = pos + 1


    if char is '*'
        type = 0
        if arena[left] is '*' or arena[right] is '*'
            type += 1
        if arena[top] is '*' or arena[bot] is '*'
            type += 2
        return (switch type
            when 0 then '+'
            when 1 then '-'
            when 2 then '|'
            when 3 then '+')
    else if char is '#'
        #      ###      \|/
        # turn ### into -*-
        #      ###      /|\
        visible = (x) -> (x is '#' or x is '#')
        
        if visible(arena[left])
            if visible(arena[right])  # middle column
                if visible(arena[top]) and visible(arena[bot])
                    return '*'
                else
                    return '|'
            else                    # right-most column
                if visible(arena[top])
                    if visible(arena[bot])
                        return '-'
                    else
                        return '\\'
                else
                    return '/'
        else    # left-most column
            if visible(arena[top])
                if visible(arena[bot])
                    return '-'
                else
                    return '/'
            else
                return '\\'


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

    xp = 2
    map = pad("Username", unameLength + xp) + "|" + (pad(key, len + xp) for key, len of statLengths).join("|")
    map += "\n" + Array(map.length + 1).join("-")

    for uname, stats of scores
        uname = pad(uname, unameLength + xp)
        stats = (pad(stats[key], len + xp) for key, len of statLengths).join("|")
        map += "\n#{uname}|#{stats}"

    return escape(map)

pad = (str, len) ->
    str = String(str)
    left = Math.floor((len - str.length) / 2) + 1
    right = Math.ceil((len - str.length) / 2) + 1
    str = Array(left).join(" ") + str + Array(right).join(" ")
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
