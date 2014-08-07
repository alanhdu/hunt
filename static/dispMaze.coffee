@render = (arena) ->
    arena += '\n'
    width = arena.indexOf('\n')
    # arena.length = height * width + (height - 1)
    height = (arena.length + 1) / (width + 1)
    
    map = ""
    for chr, i in arena
        #x = i % (width + 1)
        #y = Math.floor(i / (width + 1))
        switch chr
            #when '*'
                #c = (getType x, y, width, arena)
                #map += c
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
