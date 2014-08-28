import sockets 

class ExceptionHandler():
    # maybe we should curry/partial apply a socket instead? Seems wasteful to use a class
    def __init__(self, socket):
        self.socket = socket
    def run(self, exception, value, traceback, ns_name=""):

        if issubclass(exception, UserError):
            ns = self.socket.get_namespaces()
            ns[ns_name].emit("error", str(value))
        else:
            raise exception, value, traceback

class UserError(Exception):
    def __init__(self, uname, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)
        self.uname = uname

class UsernameTaken(UserError):
    def __init__(self, uname):
        super(UsernameTaken, self).__init__("Username {} already taken".format(uname))

class HittingAWall(UserError):
    def __init__(self, uname):
        super(HittingAWall, self).__init__("You've somehow displaced a wall")

