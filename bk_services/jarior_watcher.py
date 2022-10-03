import jarior.client
from jarior.client import Context
def run(context:Context):
    print(context.files)

jarior.client.watch(
    handler=run,
    msg_type="processing"
).start()