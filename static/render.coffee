@update = (info) ->
    render(info["arena"])

    for key in ["health", "ammo", "msg"]
        if key of info
            document.getElementById(key).innerHTML = info[key]
    null

@render = (arena) ->
    map = ""
    for chr, i in arena
        switch chr
            when '\n'
                map += "<br />"
            when ' '
                map += "&nbsp;"
            when '>'
                map += "&gt;"
            when '<'
                map += "&lt;"
            else
                map += chr

    (document.getElementById "map").innerHTML = map
