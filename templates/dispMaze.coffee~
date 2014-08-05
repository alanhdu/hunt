    s = "{{ arena | replace('\n', '\\n') }}"

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

      x = 0
      y = 0
      context.fillStyle = "#000000"
      for chr in arena
        switch chr
          when '*'
            x += 1
            context.fillRect(x * scale, y * scale, scale, scale)
          when ' '
            x += 1
          when '\n'
            y += 1
            x = 0

      
      
    render(s)
