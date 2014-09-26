from flask.ext.socketio import emit


def exception_handler(exception, value, traceback, ns_name=""):
    if issubclass(exception, UserError):
        emit("error", str(value))
    else:
        raise exception, value, traceback

class UserError(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)

class UsernameTaken(UserError):
    def __init__(self, uname):
        super(UsernameTaken, self).__init__("Username {} already taken".format(uname))

class HittingAWall(UserError):
    def __init__(self):
        super(HittingAWall, self).__init__("You've somehow displaced a wall")

