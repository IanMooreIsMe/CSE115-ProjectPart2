"""
Database related functions
"""

import sqlite3

conn = sqlite3.connect("quakes.db")
cur = conn.cursor()

def handle(func):
    """
    Handles passing around the cursor and committing changes
    """
    def wrapper(*args, **kwargs):
        """
        The wrapper for the decorated function
        """
        result = func(cur, *args, **kwargs)
        conn.commit()
        return result
    return wrapper

@handle
def initialize_db(cur):
    """
    Initializes the data base

    :param cur a cursor for the database, provided by handle
    """
    # Create the database if it doesn't exist
    cur.execute(
        "CREATE TABLE IF NOT EXISTS Quake("
        "QuakeID varchar(11) NOT NULL PRIMARY KEY , "
        "Name varchar(255) NOT NULL, "
        "Magnitude float(3) NOT NULL, "
        "Timestamp int(8) NOT NULL)"
    )
    cur.execute(
        "CREATE TABLE IF NOT EXISTS User("
        "UserID INTEGER NOT NULL PRIMARY KEY,"
        "Username varchar(60) NOT NULL UNIQUE,"
        "Password varchar(60) NOT NULL)"
    )
    cur.execute(
        "CREATE TABLE IF NOT EXISTS Game("
        "UserID int NOT NULL,"
        "QuakeID int NOT NULL,"
        "Guess int NOT NULL,"
        "Correct boolean,"  # later evaluted
        "PRIMARY KEY (UserID, QuakeID),"  # a composite primary key to allow only one guess
        "FOREIGN KEY (UserID) REFERENCES User(UserID) ON DELETE CASCADE ON UPDATE CASCADE,"
        "FOREIGN KEY (QuakeID) REFERENCES Quake(QuakeID) ON DELETE CASCADE ON UPDATE CASCADE"
        ")"
    )