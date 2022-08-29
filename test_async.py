import asyncio

async def async_func():
  import time
  time.sleep(1)
  return 1

loop = asyncio.get_event_loop()
coroutine = async_func()
r=loop.run_until_complete(coroutine)
print(r)