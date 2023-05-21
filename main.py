import asyncio
import sys
from deepdanbooru_web.src.server import app
from Shimarin.client.events import EventPolling
from deepdanbooru_web.src.client import ev
from deepdanbooru_web.src.config import USERNAME, PASSWORD


async def client():
    headers = {"username": USERNAME, "password": PASSWORD}
    async with EventPolling(ev) as poller:
        print("client started!")
        await poller.start(0.1, custom_headers=headers)


def server():
    app.run(debug=True, host="0.0.0.0", port=8080)


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
        server()
    else:
        print("Error! You need to choose server or client!")
        exit(1)


if __name__ == "__main__":
    main()
