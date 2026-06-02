import math

def cub(x):
    return x**3

def patrat(x):
    return x**2

def ecuatie_gradul_2(a, b, c):
    if a == 0:
        return "Nu este ecuatie de gradul 2"
    
    delta = b**2 - 4*a*c

    if delta < 0:
        return "Nu are solutii reale"
    
    elif delta == 0:
        x = -b/(2*a)
        return(x,)
    
    else:
        x1 = (-b + math.sqrt(delta))/(2*a)
        x2 = (-b - math.sqrt(delta))/(2*a)  
        return(x1, x2)
