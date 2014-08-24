socket = io.connect()

socket.on("error", ((err) -> alert(err)))
socket.on("update", update)

$( "#play" ).on "click", (() ->
    if window.uname is undefined
        window.uname = $( "#username" ).val()
        socket.emit('begin', {width:51, height:23, username:window.uname})
    else
        alert("Already logged in!")
)

window.onunload = ((evt) ->
    if window.uname isnt undefined
        socket.emit("logoff", {username:window.uname})
)

$( window ).keydown ((evt) ->
    if evt.target.tagName.toLowerCase() is "input" or window.uname is undefined or
      evt.ctrlKey
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

    if direction isnt undefined
        if evt.shiftKey
            type = "turn"
        else
            type = "move"
        socket.emit(type, {direction: direction, username: window.uname})
    if fire
        socket.emit("fire", {username: window.uname})
)
