import json
from Shimarin.server.events import Event, EventEmitter, CallbacksHandlers
from base64 import b64encode
from flask import Flask, render_template, request

from .config import USERNAME, PASSWORD

app = Flask(__name__)

emitter = EventEmitter()
handlers = CallbacksHandlers()
EVENTS: list[Event] = []


@app.route("/events", methods=["GET"])
async def events_route():
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
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
async def upload():
    if "file" not in request.files:
        return "No file uploaded!"

    file = request.files["file"]
    encoded = b64encode(file.stream.read()).decode("utf-8")
    event = Event.new("danbooru_new_image", encoded, json.loads)
    EVENTS.append(event)
    await emitter.send(event)
    return f'Uploaded! Go to <a href="/result?id={event.identifier}">the results page</a> to see if the result is ready!'


@app.route("/result")
async def result():
    if request.method == "GET":
        event_exists = False
        if _id := request.args.get("id"):
            for event in EVENTS:
                if event.identifier == _id:
                    event_exists = True
                    if event.answered:
                        return event.answer
                    elif event.age > 60:
                        return {
                            "error": True,
                            "message": "Event timed out! Please, try again!",
                        }
            if event_exists:
                return {
                    "error": False,
                    "message": "Waiting for server to process, this may take some time! Please, reload the page!",
                }
    return {"error": True, "message": "Invalid Event id! Please, try again!"}


if __name__ == "__main__":
    app.run(debug=True)
