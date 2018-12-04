"""
Handles dealing with the earthquake API and storing results
"""

import aiohttp
import json
import db
import game

async def get_quakes():
    """
    Gets quakes from USGS

    :return: a simplified list of 500 quakes
    """
    url = "https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&limit=500"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            raw_text = await response.text()
            raw_data = json.loads(raw_text)["features"]
            quakes = []
            for quake in raw_data:
                quake_id = quake["id"]
                quake_props = quake["properties"]
                quake_geo = quake["geometry"]["coordinates"]
                mag = quake_props["mag"]
                if (mag < 0):
                    continue
                quake = {
                    "id": quake_id,
                    "name": quake_props["title"],
                    "mag": mag,
                    "time": quake_props["time"],
                    "lat": quake_geo[1],
                    "lon": quake_geo[0]
                }
                quakes.append(quake)
            _store_quakes(quakes)
            return quakes


@db.handle
def _store_quakes(cur, quakes):
    """
    Add the quakes to the table, and let id collisions prevent duplicates

    :param cur:
    :param quakes:
    :return:
    """
    cur.executemany(
        "INSERT OR IGNORE INTO Quake (QuakeID, Name, Magnitude, Timestamp) "
        "VALUES (?, ?, ?, ?)",
        [(q["id"], q["name"], q["mag"], q["time"]) for q in quakes]
    )
    game.evaluate_games()
