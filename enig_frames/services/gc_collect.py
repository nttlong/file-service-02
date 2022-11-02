import gc

import enig


class GCCollec(enig.Singleton):
    def __init__(self):
        pass
    def clean_up(self):
        import ctypes
        gc.collect()
        libc = ctypes.CDLL("libc.so.6")
        libc.malloc_trim(0)