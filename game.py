"""
Handles the game
"""

import db
import auth
from aiohttp import web


@db.handle
def upsert_game(cur, session, guess):
    """
    Add or update a users guess for a game to the db
    :param cur: the database cursor
    :param session: the current session
    :param guess: the users guess (-1 for lower, 1 for higher)
    :return:
    """
    latest_quake = cur.execute(
        "SELECT QuakeID FROM Quake ORDER BY Timestamp DESC LIMIT 1"
    ).fetchone()[0]

    user_id = auth.get_user(session)["id"]
    if user_id is None:
        raise web.HTTPUnauthorized

    if guess not in ["-1", "1"]:
        raise web.HTTPBadRequest

    cur.execute(
        "INSERT OR REPLACE INTO Game (UserID, QuakeID, Guess) "
        "VALUES (?, ?, ?)",
        (user_id, latest_quake, guess)
    )

    raise web.HTTPOk

@db.handle
async def get_leaderboard(cur):
    """
    Returns a json to be used for the leaderboard
    """
    scores = cur.execute(
        "SELECT u.Username, SUM(g.Correct) AS Score "
        "FROM Game g "
        "INNER JOIN User u ON u.UserID = g.UserID "
        "GROUP BY u.UserID "
        "ORDER BY Score DESC "
        "LIMIT 5"
    )
    leaderboard = []
    for score in scores:
        if score[0] is not None:
            leaderboard.append({"username": score[0], "score": score[1] or 0})
    return leaderboard

@db.handle
async def get_history(cur, session):
    """
    Returns a users game history
    """
    user_id = auth.get_user(session)["id"]
    games = []

    if user_id is not None:
        played_games = cur.execute(
            "SELECT q.Name, q.Timestamp, g.Guess, g.Correct "
            "FROM Game g "
            "INNER JOIN Quake q ON q.QuakeID = g.QuakeID "
            "WHERE g.UserID = ? "
            "ORDER BY q.Timestamp DESC",
            (user_id,)
        )
        for game in played_games:
            games.append({
                "name": game[0],
                "timestamp": game[1],
                "guess": game[2],
                "correct": game[3]
            })

    return games

@db.handle
def evaluate_games(cur):
    """
    Evaluates games that haven't been scored yet
    """
    unevaluated = cur.execute(
        "SELECT g.UserID, g.QuakeID, q.Magnitude, q.Timestamp, g.Guess "
        "FROM Game g "
        "INNER JOIN Quake q ON q.QuakeID = g.QuakeID "
        "WHERE Correct IS NULL"
    )

    for game in unevaluated:
        timestamp = game[3]
        future = cur.execute(
            "SELECT Magnitude "
            "FROM Quake "
            "WHERE Timestamp > ?",
            (timestamp,)
        ).fetchone()

        if future is None:
            continue  # the game has not finished yet

        user_id = game[0]
        quake_id = game[1]
        guess = game[4]
        previous_mag = game[2]
        future_mag = future[0]
        result = (previous_mag < future_mag) - (previous_mag > future_mag)
        correct = (result == guess or result == 0)  # if there's no difference, give win anyways

        cur.execute(
            "UPDATE Game "
            "SET Correct = ? "
            "WHERE UserID = ? AND QuakeID = ?",
            (correct, user_id, quake_id)
        )
