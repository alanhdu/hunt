$( "#square" ).on "click", (() ->
    if $("#square").prop("checked")
        $(".rect").removeClass("rect").addClass("square")
    else
        $(".square").removeClass("square").addClass("rect")
    return null
)

@update = (info) ->
    document.getElementById("scores").innerHTML = getScoreboard(info["scores"])
    document.getElementById("arena").innerHTML = displayArena(info.player["arena"], info.player["x"], info["y"])

    for key in ["msg", "cloak", "scan"]
        if key of info.player
            document.getElementById(key).innerHTML = escape(info.player[key])
    for key in ["health", "ammo"]
        document.getElementById(key).innerHTML = formatNumber(info.player[key])
    return null

@clear = () ->
    for key in ["health", "ammo", "msg", "arena", "scores", "cloak", "scan"]
        document.getElementById(key).innerHTML = ""
    return null

height = 0
width = 0

displayArena = (arena, curX, curY) ->
    x = 0
    y = 0
    str = ""
    height = (arena.split("\n").length)
    width = (arena.length - height + 1) / height

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

getPos = (x, y) -> y * (width + 1) + x

getType = (char, arena, x , y) ->
    if char isnt "#" and char isnt "*"
        return char

    pos = getPos(x, y)
    top = getPos(x, y - 1)
    bot = getPos(x, y + 1)
    left = getPos(x - 1, y)
    right = getPos(x + 1, y)

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
        visible = (x) -> (x is '#')
        
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
            stat = formatNumber(stat)
            if key not of statLengths or stat.length > statLengths[key]
                statLengths[key] = stat.length

    xp = 2
    map = pad("Username", unameLength + xp) + "|" + (pad(key, len + xp) for key, len of statLengths).join("|")
    map += "\n" + Array(map.length + 1).join("-")

    for uname, stats of scores
        uname = pad(uname, unameLength + xp)
        stats = (pad(formatNumber(stats[key]), len + xp) for key, len of statLengths).join("|")
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

formatNumber = (num) ->
    Number(num).toFixed(2)
