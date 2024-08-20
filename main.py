import asyncio
import sys

from deepdanbooru_web.src.client import ev
from deepdanbooru_web.src.config import (PASSWORD, SERVER_ENDPOINT,
                                         SERVER_PORT, USERNAME)


async def client():
    from Shimarin.client.events import EventPolling
    headers = {"username": USERNAME, "password": PASSWORD}
    async with EventPolling(ev) as poller:
        print("client started!")
        await poller.start(0.5, custom_headers=headers, server_endpoint=SERVER_ENDPOINT)


async def server():
    from deepdanbooru_web.src.server import app
    from hypercorn import Config
    from hypercorn.asyncio import serve

    config = Config()
    config.accesslog = "-"
    config.errorlog = "-"
    config.bind = f"0.0.0.0:{SERVER_PORT}"
    await serve(app, config)


def main():
    if len(sys.argv) < 2:
        print("Error! You need to choose server or client!")
        exit(1)
    arg = sys.argv[1]
    if arg == "client":
        loop = asyncio.get_event_loop()
        task = loop.create_task(client())
        loop.run_until_complete(asyncio.gather(task))
        loop.run_forever()
    elif arg == "server":
        asyncio.run(server())
    else:
        print("Error! You need to choose server or client!")
        exit(1)


if __name__ == "__main__":
    main()
