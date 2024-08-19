import hashlib
import json
import logging
from base64 import b64encode

from flask import Flask, render_template, request
from Shimarin.server.events import Event, EventEmitter
from Shimarin.plugins.flask_api import ShimaApp, CONTEXT_PATH
from werkzeug import serving

from .db import *

parent_log_request = serving.WSGIRequestHandler.log_request
app = Flask(__name__)
emitter = EventEmitter()
app.register_blueprint(ShimaApp(emitter))
EVENTS: list[Event] = []

werkzeug_log = logging.getLogger("werkzeug")

@app.route(CONTEXT_PATH + "/")
async def index():
    werkzeug_log.disabled = False
    return render_template("index.html")

@app.route(CONTEXT_PATH + "/upload", methods=["POST"])
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


@app.route(CONTEXT_PATH + "/result")
async def result():
    werkzeug_log.disabled = False
    if request.method != "GET":
        return {"error": True, "message": "Invalid request method!"}
    _id = request.args.get("id")
    if not _id:
        return {"error": True, "message": "Invalid Event ID! Please try again!"}
    print("get tags")
    tags = get_tags(_id)
    if tags:
        return {"ok": True, "tags": json.loads(tags)}
    for event in EVENTS:
        if event.identifier != _id:
            continue
        if event.answered:
            answer = event.answer
            print(answer)
            if answer['ok']:
                update_tags(event_id=event.identifier, tags=json.dumps(answer['tags']))
                return answer
            return {"error": True, "message": answer['message']}
        if event.age > 60:
            return {"error": True, "message": "Event timed out! Please try again!"}
        return {
            "error": False,
            "message": "Waiting for the server to process. This may take some time. Please reload the page!",
        }
    return {"error": True, "message": "Invalid Event ID! Please try again!"}


if __name__ == "__main__":
    app.run(debug=True)
