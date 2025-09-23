def fact(n):
    if n == 0: 
        return 0
    return fact(n-1)*n 

print(fact(3))