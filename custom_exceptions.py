class UserError(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)


class UsernameTaken(UserError):
    def __init__(self, uname):
        s = "Username {} is already taken".format(uname)
        super(UsernameTaken, self).__init__(s)


class AlreadyLoggedIn(UserError):
    def __init__(self):
        s = "You're already logged in!"
        super(AlreadyLoggedIn, self).__init__(s)


class HittingAWall(UserError):
    def __init__(self):
        super(HittingAWall, self).__init__("You've somehow displaced a wall")
