socket = io.connect()
# TODO add actual usernames/ids
#socket.on("connect", () -> socket.emit('begin', {width:64, height:48, username:"test"}))
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

    evt.preventDefault()
    if evt.shiftKey
        type = "turn"
    else
        type = "move"

    switch chr
        when 'J' then direction = 'v'
        when 'K' then direction = '^'
        when 'L' then direction = '>'
        when 'H' then direction = '<'

    if direction isnt undefined
        username = window.username
        socket.emit(type, {direction: direction, username: username})
)
