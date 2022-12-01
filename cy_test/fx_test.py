def Fx(a):
    if a==1:
        return  a
    elif a==0:
        return a
    else:
        return Fx(a-1)+Fx(a-2)
