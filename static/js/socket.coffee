socket = io.connect()

socket.on("python_error", ((err) -> alert(err)))
socket.on("update", update)
socket.on("acknowledged", (info) ->
    window.uname = $("#username").val())

socket.on("disconnect", () ->
    window.uname = undefined
    clear()
    document.getElementById("status").innerHTML = "Disconnected from server"
    return null
)

$("#play").on("click", (() ->
    if window.uname is undefined
        socket.emit('begin', {width:51, height:23, username:$("#username").val()})
    else
        alert("Already logged in!")
    return null
    )
)

$(window).keydown ((evt) ->
    tag = evt.target.tagName.toLowerCase()
    if tag is "input" or window.uname is undefined or evt.ctrlKey
        return true

    key = evt.which
    chr = String.fromCharCode key

    switch chr
        when 'J' then direction = 'v'
        when 'K' then direction = '^'
        when 'L' then direction = '>'
        when 'H' then direction = '<'
        when 'F' then fire = true
        when 'S' then scan = true
        when 'C' then cloak = true
        else
            return true

    evt.preventDefault()

    if direction isnt undefined
        if evt.shiftKey
            type = "turn"
        else
            type = "move"
        socket.emit(type, direction)
    else if fire
        if evt.shiftKey
            type = "bomb"
        else
            type = "fire"
        socket.emit(type)
    else if scan
        socket.emit("scan")
    else if cloak
        socket.emit("cloak")
    return null
)
