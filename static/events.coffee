socket = io.connect()

socket.on("frame", render)
socket.on("error", ((err) -> alert(err)))
socket.on("update", render)

$( "#play" ).on "click", (() ->
    window.username = $( "#username" ).val()
    socket.emit('begin', {width:51, height:23, username:username})
)

$( window ).keydown ((evt) ->
    if evt.target.tagName.toLowerCase() is "input"
        return true

    key = evt.which
    chr = String.fromCharCode key

    switch chr
        when 'J' then direction = 'v'
        when 'K' then direction = '^'
        when 'L' then direction = '>'
        when 'H' then direction = '<'
        when 'F' then fire = true
        else
            return true

    evt.preventDefault()
    username = window.username

    if direction isnt undefined
        if evt.shiftKey
            type = "turn"
        else
            type = "move"
        socket.emit(type, {direction: direction, username: username})
    if fire
        console.log("Firing")
        socket.emit("fire", {username: username})
)
