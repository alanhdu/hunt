@update = (info) ->
    unameLength = "Username".length
    statLengths = {}

    for key, stat of info["scores"][window.uname]
        statLengths[key] = key.length
    for uname, stats of info["scores"]
        if uname.length > unameLength
            unameLength = uname.length
        for key, stat of stats
            stat = String(stat)
            if key not of statLengths or stat.length > statLengths[key]
                statLengths[key] = stat.length

    map = pad("Username", unameLength) + "|" + (pad(key, len) for key, len of statLengths).join("|")
    map += "\n" + Array(map.length + 1).join("-")

    for uname, stats of info["scores"]
        uname = pad(uname, unameLength)
        stats = (pad(stats[key], len) for key, len of statLengths).join("|")
        console.log(uname.length)
        console.log(pad("Username", unameLength).length)
        map += "\n#{uname}|#{stats}"

    document.getElementById("scores").innerHTML = escape(map)

    for key in ["health", "ammo", "msg", "arena"]
        if key of info
            document.getElementById(key).innerHTML = escape(info[key])
    null

@pad = (str, len) ->
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
