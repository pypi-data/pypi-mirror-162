from .import cols

def __setup__ (app, mntopt):
    app.mount ("/cols", cols)
