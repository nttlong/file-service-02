import asyncio
from asyncio import coroutine
import time
async def test(a):
    time.sleep(1)
    return a+1


result = asyncio.get_event_loop().run_until_complete(test(10))
print(result)