render = (arena) ->
    arena += '\n'
    width = arena.indexOf('\n')
    # arena.length = height * width + (height - 1)
    height = (arena.length + 1) / (width + 1)

    console.log arena
    
    x = 0
    y = 0
    map = ""
    for chr in arena
        beginSpan = "<span id='" + x + "-" + y + "'>"
        switch chr
            when '*'
                c = (getType x, y, width, arena)
                map += beginSpan + c + "</span>"
                x++
            when '\n'
                map += "<br />"
                x=0
                y++
            when ' '
                map += beginSpan + "&nbsp;" + "</span>"
                x++
            when '>'
                map += beginSpan + "&gt;" + "</span>"
                x++
            when '<'
                map += beginSpan + "&lt;" + "</span>"
                x++
            else
                map += beginSpan + chr + "</span>"

    (document.getElementById "map").innerHTML = map


getType = (x, y, width, arena) ->
    w = width + 1
    pos = w * y + x
    top = pos - w
    bot = pos + w
    left = pos - 1
    right = pos + 1
    if arena[left] is '*' or arena[right] is '*'
        dash = true
    if arena[top] is '*' or arena[bot] is '*'
        pipe = true
    if arena[top] isnt '*' and arena[bot] isnt '*' and
       arena[left] isnt '*' and arena[right] isnt '*'
        pipe = true
        dash = true
    
    if pipe and dash
        return '+'
    else if pipe
        return '|'
    else if dash
        return '-'
    else
        return ' '
