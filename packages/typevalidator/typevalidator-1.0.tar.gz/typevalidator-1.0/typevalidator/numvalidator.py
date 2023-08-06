def ifint(object):
    if isinstance(object, int) == True:
        return True
    else:
        return False

def iffloat(object):
    if isinstance(object, float) == True:
        return True
    else:
        return False 

def ifstring(object):
    if isinstance(object, str) == True:
        return True
    else:
        return False 

def iflist(object):
    if isinstance(object, list) == True:
        return True
    else:
        return False 

def ifdict(object):
    if isinstance(object, dict) == True:
        return True
    else:
        return False

def ifbool(object):
    if isinstance(object, bool) == True:
        return True
    else:
        return False  

def iftuple(object):
    if isinstance(object, tuple) == True:
        return True
    else:
        return False 


if __name__ == "__main__":
    # Examples
    if ifint(1.0) == True:
        pass # It is an int
    else:
        pass # It is not an int (In this Szeanrio right!)