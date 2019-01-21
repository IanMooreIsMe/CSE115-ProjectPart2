"""
The main entry point for the web server
"""

from aiohttp import web
import time
import base64
from cryptography import fernet
from aiohttp_session import setup, get_session
from aiohttp_session.cookie_storage import EncryptedCookieStorage
import quakes
import db
import auth
import game
import configparser

routes = web.RouteTableDef()
config = configparser.ConfigParser()

@routes.get("/")
async def index(request):
    """
    Provide the index.html at the root
    """
    return web.FileResponse("static/index.html")

@routes.post("/user")
async def user_post(request):
    """
    Handle login, logout, and account creation
    """
    session = await get_session(request)
    data = await request.post()
    action = data.get("action")

    if action == "create" or action == "login":
        username = data.get("username")
        password = data.get("password")

        if (username is None or password is None):
            raise web.HTTPBadRequest

        if action == "create":
            auth.create_account(session, username, password)
        elif action == "login":
            auth.login(session, username, password)
    elif action == "logout":
        auth.logout(session)

    raise web.HTTPOk

@routes.get("/user")
async def user_get(request):
    """
    Allow users to query the current login status
    """
    session = await get_session(request)
    user = auth.get_user(session, strip_id=True)
    return web.json_response(user)

@routes.post("/game")
async def game_post(request):
    """
    Handle game guesses
    """
    session = await get_session(request)
    data = await request.post()
    guess = data.get("guess")
    game.upsert_game(session, guess)

@routes.get("/game")
async def game_get(request):
    """
    Allows users to grab stats on the game
    """
    session = await get_session(request)
    leaderboard = await game.get_leaderboard()
    history = await game.get_history(session)
    payload = {"leaderboard": leaderboard, "history": history}
    return web.json_response(payload)

@routes.get("/quakes")
async def quakes_api(request):
    """Returns the data from the GeoJSON quakes API"""
    # prevent too many refreshes too quickly
    session = await get_session(request)
    current_ms = time.time()
    last_refresh = session["last_refresh"] if "last_refresh" in session else 0
    ratelimited = last_refresh > (current_ms - 10)  # 10 second timeout

    if not ratelimited:
        session["last_refresh"] = current_ms
        data = await quakes.get_quakes()
        return web.json_response(data)
    else:
        raise web.HTTPTooManyRequests

@routes.get("/mapbox")
async def mapbox_token(request):
    """Returns the mapbox token from the config"""
    mapbox = config["mapbox"]
    return web.json_response({
        "token": mapbox["token"]
    })


def make_app():
    """Neatly creates the webapp"""
    app = web.Application()
    config.read("config.cfg")
    fernet_key = fernet.Fernet.generate_key()
    secret_key = base64.urlsafe_b64decode(fernet_key)
    setup(app, EncryptedCookieStorage(secret_key, cookie_name="session"))
    routes.static("/", "static")
    app.add_routes(routes)
    db.initialize_db()
    return app


web.run_app(make_app())