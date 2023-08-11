from uuid import uuid4

from socketio import ASGIApp, AsyncServer
from uvicorn import run

sio = AsyncServer(async_mode="asgi")
app = ASGIApp(sio)


@sio.event
def connect(sid, environ):
    print("connect ", sid)


@sio.event
def disconnect(sid):
    print("disconnect ", sid)


@sio.event
def discordMessage(sid, data):
    print(f"\nServer: {data}")
    return str(uuid4())


run(app, port=2087)
