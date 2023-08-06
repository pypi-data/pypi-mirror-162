# calc module 

def add(a,b):
    return a+b

def mul(a,b):
    """_summary_
    bla bla bal
    Parameters
    ----------
    a : _type_
        _description_
    b : _type_
        _description_

    Returns
    -------
    _type_
        _description_
    """
    return a*b

def div(a,b):
    if b!=0:
        return a/b

def minus(a,b):
    return a-b

class NoArgumentsException(BaseException):
    def __init__(self,message):
        super().__init__(message)
        
if __name__ == "__main__":
    import sys
    try:
        param1=sys.argv[1]    
        param2=sys.argv[2]
        print(add(int(param1),int(param2)))
    except:
        raise NoArgumentsException("usage: python -m calc <arg1> <arg2>")