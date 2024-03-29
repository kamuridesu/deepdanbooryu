import os
from tempfile import NamedTemporaryFile
from base64 import b64decode
from Shimarin.client.events import EventsHandlers, Event
from .docker import start_deepdanbooru


ev = EventsHandlers()
os.makedirs("temp", exist_ok=True)
INSTANCES = {"total": 0, "running": 0, "max": 10}


@ev.new("danbooru_new_image")
async def process_image(event: Event):
    response = {"ok": False}
    payload = b""
    temp_dir = os.path.join("temp", event.identifier)
    try:
        os.makedirs(temp_dir)
    except Exception:
        response = {
            "ok": False,
            "message": "Error creating temp dir! Please try again!",
        }
    try:
        tags = []
        with NamedTemporaryFile("wb", dir=temp_dir, suffix=".jpg", delete=True) as file:
            payload = b64decode(event.payload.encode("utf-8"))
            file.write(payload)
            while True:
                if INSTANCES["running"] < INSTANCES["max"]:
                    INSTANCES["running"] += 1
                    INSTANCES["total"] += 1
                    tags = await start_deepdanbooru(temp_dir, event.identifier)
                    INSTANCES["running"] -= 1
                    break
        os.rmdir(temp_dir)
        response = {"ok": True, "tags": tags}
    except ValueError as e:
        if "DOCKER_HOST" in str(e):
            response['message'] = "Failed to start Docker engine! Please, contact the admin and read the logs."
        else:
            response['message'] = f"Failed: {e}"
    except Exception as e:
        response = {"ok": False, "message": f"An error occured: {e}"}
    return await event.reply(response)
