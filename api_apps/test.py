



def TiengViet(langue, *args,**kwargs):
    def re_mody(*_args,**_kwargs):
        ham_goc= _args[0]
        def ham_moi(*__args,**__kwargs):
            print("xin chao"+__args[0])
        return ham_moi
    return re_mody
@TiengViet(langue="vie")
def hello(name):
    print("Hello:"+name)
hello("Thuan")