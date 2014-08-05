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
        switch chr
            when '*'
                c = (getType x, y, width, arena)
                map += "<span id=\"" + x + "-" + y + "\">" + c + "</span>"
                x++
            when ' '
                map += "<span id=\"" + x + "-" + y + "\">&nbsp;</span>"
                x++
            when '\n'
                map += "<br />"
                x=0
                y++

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
    
    if pipe and dash
        return '+'
    else if pipe
        return '|'
    else if dash
        return '-'
    else
        return ' '
