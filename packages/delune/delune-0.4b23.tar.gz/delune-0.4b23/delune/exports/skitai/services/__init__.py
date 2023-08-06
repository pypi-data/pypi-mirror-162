from .import cols

def __setup__ (context, app, opts):
    app.mount ("/cols", cols)
