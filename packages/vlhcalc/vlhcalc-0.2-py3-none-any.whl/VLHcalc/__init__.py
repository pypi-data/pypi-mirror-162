def add(a,b):
    return a+b

def sub(a,b):
    return a-b

def mul(a,b):
    return a*b

def div(a,b):
    return a/b

def exp(a,b):
    return a**b

def abs(a,b):
    if a < b:
        a, b = b, a
    return a - b

def log(a, b):
    if a < b:
        return 0  
    return 1 + log(a/b, b)