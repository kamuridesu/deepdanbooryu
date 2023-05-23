import hashlib
import json
import logging
from base64 import b64encode

from flask import Flask, render_template, request
from Shimarin.server.events import CallbacksHandlers, Event, EventEmitter
from werkzeug import serving

from .config import PASSWORD, USERNAME
from .db import *

parent_log_request = serving.WSGIRequestHandler.log_request
app = Flask(__name__)

emitter = EventEmitter()
handlers = CallbacksHandlers()
EVENTS: list[Event] = []

werkzeug_log = logging.getLogger("werkzeug")


@app.route("/events", methods=["GET"])
async def events_route():
    werkzeug_log.disabled = True
    if (username := request.headers.get("username")) and (
        password := request.headers.get("password")
    ):
        if username != USERNAME or password != PASSWORD:
            return {"ok": False, "message": "Invalid credentials!"}, 401
    else:
        return {"ok": False, "message": "Invalid credentials!"}, 401
    fetch = request.args.get("fetch")
    events_to_send = 1
    if fetch:
        events_to_send = int(fetch)
    events = []
    for _ in range(events_to_send):
        last_ev = await emitter.fetch_event()
        if last_ev.event_type:
            await handlers.register(last_ev)
            events.append(last_ev.json())
    return events


@app.route("/callback")
async def reply_route():
    werkzeug_log.disabled = False
    if (username := request.headers.get("username")) and (
        password := request.headers.get("password")
    ):
        if username != USERNAME or password != PASSWORD:
            return {"ok": False, "message": "Invalid credentials!"}, 401
    else:
        return {"ok": False, "message": "Invalid credentials!"}, 401
    data = request.get_json(silent=True)
    if data:
        identifier = data["identifier"]
        payload = data["payload"]
        await handlers.handle(identifier, payload)
    return {"ok": True}


@app.route("/")
async def index():
    werkzeug_log.disabled = False
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
async def upload():
    werkzeug_log.disabled = False
    if "file" not in request.files:
        return "No file uploaded!"
    file_bytes = request.files["file"].stream.read()
    _hash = hashlib.md5(file_bytes).hexdigest()
    encoded = b64encode(file_bytes).decode("utf-8")
    if not (event_id := get_event_id(_hash)):
        event = Event.new("danbooru_new_image", encoded, json.loads)
        EVENTS.append(event)
        await emitter.send(event)
        store_event(event.identifier, _hash)
        event_id = event.identifier
    return f'Uploaded! Go to <a href="/result?id={event_id}">the results page</a> to see if the result is ready!'


@app.route("/result")
async def result():
    werkzeug_log.disabled = False
    if request.method == "GET":
        event_exists = False
        if _id := request.args.get("id"):
            print("get tags")
            tags = get_tags(_id)
            if tags:
                return {"ok": True, "tags": json.loads(tags)}
            for event in EVENTS:
                if event.identifier == _id:
                    event_exists = True
                    print("event answred")
                    if event.answered:
                        print("get event answer")
                        answer = event.answer
                        print("update tags")
                        update_tags(event_id=event.identifier, tags=json.dumps(answer['tags']))
                        return answer
                    elif event.age > 60:
                        return {
                            "error": True,
                            "message": "Event timed out! Please try again!",
                        }
            if event_exists:
                return {
                    "error": False,
                    "message": "Waiting for the server to process. This may take some time. Please reload the page!",
                }
    return {"error": True, "message": "Invalid Event ID! Please try again!"}


if __name__ == "__main__":
    app.run(debug=True)
