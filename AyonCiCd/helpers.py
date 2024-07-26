class FaileException(Exception):
    pass

def FAIL(fail_msg:str):
    raise FaileException(fail_msg)
