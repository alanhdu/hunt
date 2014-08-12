socket = io.connect()

socket.on("frame", render)
socket.on("error", ((err) -> alert(err)))
socket.on("ack user", (() -> setInterval (() -> requestUpdate()), 150))

requestUpdate = () ->
    socket.emit("request frame", {username:window.username})

$( "#play" ).on "click", (() ->
    window.username = $( "#username" ).val()
    socket.emit('begin', {width:51, height:23, username:username})
)

$( window ).keydown ((evt) ->
    if evt.target.tagName.toLowerCase() is "input"
        return true

    key = evt.which
    chr = String.fromCharCode key

    if evt.shiftKey
        type = "turn"
    else
        type = "move"

    switch chr
        when 'J' then direction = 'v'
        when 'K' then direction = '^'
        when 'L' then direction = '>'
        when 'H' then direction = '<'
        else return true

    evt.preventDefault()
    if direction isnt undefined
        username = window.username
        socket.emit(type, {direction: direction, username: username})
)
