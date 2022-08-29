import  cython
@cython.cfunc
def add(l: cython.int, f: cython.int) -> cython.int:
    return  l+f*2
print("cong 2 so  nung van sua dc ok {}".format(add(5,5)))

def show():
    raise Exception("Loi")

