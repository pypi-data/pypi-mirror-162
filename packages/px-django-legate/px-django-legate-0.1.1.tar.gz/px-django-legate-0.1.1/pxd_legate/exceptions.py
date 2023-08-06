class LegateError(Exception):
    pass


class CheckError(LegateError):
    pass


class NoCheckers(CheckError):
    pass
