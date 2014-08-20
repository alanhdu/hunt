@update = (info) ->
    render(info["arena"])
    document.getElementById("health").innerHTML = info["health"]
    document.getElementById("ammo").innerHTML = info["ammo"]

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
