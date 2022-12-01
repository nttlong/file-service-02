from datetime import datetime
def Fx(a):
    if a==1:
        return  a
    elif a==0:
        return a
    else:
        return Fx(a-1)+Fx(a-2)


import  fx_test
t = datetime.utcnow()
v = fx_test.Fx(10)
n = (datetime.utcnow()-t).total_seconds()*1000
print(n)
t = datetime.utcnow()
v = Fx(10)
n = (datetime.utcnow()-t).total_seconds()*1000
print(n)