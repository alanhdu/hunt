s = "{{ arena | replace('\n', '\\n') }}"
s = s + "\n"
#s = "** * **\n** * **\n** * **\n** * **\n** * **\n"

render = (arena, scale=10) ->
    width = arena.indexOf('\n')
    # arena.length = height * width + (height - 1)
    height = (arena.length + 1) / (width + 1)
    canvas = document.getElementById("game")
    context = canvas.getContext("2d")

    if height * scale == canvas.height and width * scale == canvas.width
        context.clearRect(0, 0, canvas.width, canvas.height)
    else
        canvas.width = width * scale
        canvas.height = height * scale
        context.clearRect(0, 0, canvas.width, canvas.height)

    x = 0
    y = 0
    context.fillStyle = "#000000"
    for chr in arena
        switch chr
            when '*'
                draw x * scale, y * scale, scale, scale, (getType x, y, width, arena), context
                x += 1
            when ' '
                x += 1
            when '\n'
                y += 1
                x = 0

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
        return 'plus'
    else if pipe
        return 'pipe'
    else if dash
        return 'dash'

draw = (x, y, width, height, type, context) ->
    if type is 'plus'
        draw x, y, width, height, 'pipe', context
        draw x, y, width, height, 'dash', context
        return

    switch type
        when 'pipe'
            x1 = x + (width/2) - 1
            y1 = y
            w = 2
            h = height
        when 'dash'
            x1 = x
            y1 = y + (height/2) - 1
            w = width
            h = 2
    
    context.fillRect x1, y1, w, h

render(s)
