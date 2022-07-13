from busboard.controllers.busboard import busboardRoutes


def register_controllers(app):
    busboardRoutes(app)
