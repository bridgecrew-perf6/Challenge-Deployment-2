from multiprocessing import connection
from typing import Tuple
import mariadb
import toml
import pathlib
import logging

from game import Game


# Read local `config.toml` file.
config = toml.load(pathlib.Path(__file__).parent / "dbcredentials.toml")


def main():
    return


def connect():
    try:
        conn = mariadb.connect(
            user=config["DB"]["username"],
            password=config["DB"]["password"],
            host=config["DB"]["ipaddress"],
            port=config["DB"]["port"],
            database=config["DB"]["dbname"],
        )
        return conn

    except mariadb.Error as e:
        logging.error(f"{__name__:<15} connecting to MariaDB Platform: {e}")
        return


def disconnect(_connection):
    _connection.close()
    return


def insert_games(_games: list[Game], _connection) -> None:
    for game in _games:
        insert_game(game, _connection)

    return


def insert_game(_game: Game, _connection) -> bool:

    # Insert Game into Database
    SQL = (
        "INSERT INTO Games (ID, NAME, Description, Price, Developer, Win_Support, Mac_Support, Linux_Support, Pos_Review, Neg_Review )"
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
    )

    cursor = _connection.cursor()
    try:
        cursor.execute(
            SQL,
            (
                _game.id,
                _game.name,
                _game.description,
                _game.price,
                _game.developer,
                _game.win_support,
                _game.mac_support,
                _game.linux_support,
                _game.positive_reviews,
                _game.negative_reviews,
            ),
        )

    except mariadb.IntegrityError:
        logging.debug(f"{__name__:<15} Inserting {_game.name} already inserted")

    except Exception as e:
        logging.error(f"{__name__:<15} Inserting {e}")

    # Insert Game_Genre into Database
    genres = _game.genres
    for genre in genres:
        SQL = "INSERT INTO `Game-Genres` (Game_ID, Genre_ID) VALUES (?, ?)"

        try:
            cursor.execute(SQL, (_game.id, genre[0]))

        except Exception as e:
            logging.error(
                f"{__name__:<15} Inserting game {_game.name} - genre {genre[1]}  {e}"
            )

    # Insert Game_Category into Database
    categories = _game.categories
    for category in categories:
        SQL = "INSERT INTO `Game-Categories` (Game_ID, Category_ID) VALUES (?, ?)"

        try:
            cursor.execute(SQL, (_game.id, category[0]))

        except Exception as e:
            logging.error(
                f"{__name__:<15} Inserting game {_game.name} - category {category[1]}  {e}"
            )

    _connection.commit()

    return


def insert_genres(
    _genres: list[Tuple[int, str]], _connection
) -> None:
    cursor = _connection.cursor()

    # Insert Genres into Database
    SQL = "INSERT INTO Genres (ID, Description) VALUES (?, ?)"

    for genre in _genres:
        try:
            cursor.execute(SQL, (genre[0], genre[1]))
            _connection.commit()

        except mariadb.IntegrityError:
            logging.debug(f"{__name__:<15} Inserting genres{genre[1]} already inserted")

        except Exception as e:
            logging.error(f"{__name__:<15} Inserting genre {genre[1]} {e}")


def insert_categories(
    _categories: list[Tuple[int, str]], _connection
) -> None:
    cursor = _connection.cursor()

    # Insert Categories into Database
    SQL = "INSERT INTO Categories (ID, Description) VALUES (?, ?)"

    for category in _categories:
        try:
            cursor.execute(SQL, (category[0], category[1]))

        except mariadb.IntegrityError:
            logging.debug(
                f"{__name__:<15} Inserting categories {category[1]} already inserted"
            )

        except Exception as e:
            logging.error(f"{__name__:<15} Inserting categories{category[1]} {e}")


def get_games(_connection) -> list[dict[int, str]]:
    cursor = _connection.cursor()
    SQL = "SELECT ID, Name FROM Games"
    cursor.execute(SQL)
    results = []
    temp = []
    for result in cursor:
        results.append(result)

    for result in results:
        temp.append({result[1]: result[0]})

    results = temp

    return results


def get_game_by_id(_id: int, _connection) -> Game:
    cursor = _connection.cursor()
    SQL = "SELECT * FROM Games WHERE ID = ?"
    cursor.execute(SQL, (_id,))

    game_data = []
    for result in cursor:
        game_data.append(result)

    game = Game(
        game_data[0][0],
        game_data[0][1],
        game_data[0][2],
        game_data[0][3],
        game_data[0][4],
        game_data[0][5],
        game_data[0][6],
        game_data[0][7],
        game_data[0][8],
        game_data[0][9],
    )

    return game


def get_genres(_connection) -> list[dict[int, str]]:
    cursor = _connection.cursor()
    SQL = "SELECT ID, Description FROM Genres"
    cursor.execute(SQL)
    results = []
    temp = []

    for result in cursor:
        results.append(result)

    for result in results:
        temp.append({result[1]: result[0]})

    results = temp
    return results


def get_genre_games(
    _genre_id: int, _connection
) -> list[dict[int, str]]:
    cursor = _connection.cursor()
    SQL = "SELECT ID, Name FROM Games WHERE ID IN (SELECT Game_ID FROM `Game-Genres` WHERE Genre_ID = ?)"
    cursor.execute(SQL, (_genre_id,))
    results = []
    temp = []
    for result in cursor:
        results.append(result)

    for result in results:
        temp.append({result[1]: result[0]})

    results = temp
    return results


def get_category_games(
    _category_id: int, _connection
) -> list[dict[int, str]]:
    cursor = _connection.cursor()
    SQL = "SELECT ID, Name FROM Games WHERE ID IN (SELECT Game_ID FROM `Game-Categories` WHERE Category_ID = ?)"
    cursor.execute(SQL, (_category_id,))
    results = []
    temp = []
    for result in cursor:
        results.append(result)

    for result in results:
        temp.append({result[1]: result[0]})

    results = temp
    return results


def get_game_ratings(
    _game_id: int, _connection
) -> list[Tuple[int, int]]:
    cursor = _connection.cursor()
    SQL = "SELECT Pos_Review, Neg_Review FROM Games WHERE ID = ?"
    cursor.execute(SQL, (_game_id,))
    results = []

    for result in cursor:
        results.append(result)

    return results


def get_supported_platforms(
    _game_id: int, _connection
) -> list[Tuple[bool, bool, bool]]:
    cursor = _connection.cursor()
    SQL = "SELECT Win_Support, Mac_Support, Linux_Support FROM Games WHERE ID = ?"
    cursor.execute(SQL, (_game_id,))
    results = []
    for result in cursor:
        results.append(result)
    return results


def get_categories(_connection) -> list[dict[int, str]]:
    cursor = _connection.cursor()
    SQL = "SELECT ID, Description FROM Categories"
    cursor.execute(SQL)
    results = []
    temp = []

    for result in cursor:
        results.append(result)

    for result in results:
        temp.append({result[1]: result[0]})

    results = temp
    return results


def get_categories_count(_connection) -> list[str, int]:
    cursor = _connection.cursor()
    SQL = "SELECT (SELECT Description FROM Categories WHERE ID = Category_ID), COUNT(Game_ID) FROM `Game-Categories` GROUP BY Category_ID"
    cursor.execute(SQL)
    results = []

    for result in cursor:
        results.append(result)
    return results


def get_genres_count(_connection) -> list[str, int]:
    cursor = _connection.cursor()
    SQL = "SELECT (SELECT Description FROM Genres WHERE ID = Genre_ID), COUNT(Game_ID) FROM `Game-Genres` GROUP BY Genre_ID"
    cursor.execute(SQL)
    results = []

    for result in cursor:
        results.append(result)
    return results


def get_games_by_genre(
    _genre_id: int, _connection
) -> list[dict[int, str]]:
    cursor = _connection.cursor()
    SQL = "SELECT ID, Name FROM Games WHERE ID IN (SELECT Game_ID FROM `Game-Genres` WHERE Genre_ID = ?)"
    cursor.execute(SQL, (_genre_id,))
    results = []
    temp = []
    for result in cursor:
        results.append(result)

    for result in results:
        temp.append({result[1]: result[0]})

    results = temp
    return results


def get_games_by_category(
    _category_id: int, _connection
) -> list[dict[int, str]]:
    cursor = _connection.cursor()
    SQL = "SELECT ID, Name FROM Games WHERE ID IN (SELECT Game_ID FROM `Game-Categories` WHERE Category_ID = ?)"
    cursor.execute(SQL, (_category_id,))
    results = []
    temp = []
    for result in cursor:
        results.append(result)

    for result in results:
        temp.append({result[1]: result[0]})

    results = temp
    return results


def get_game_categories(
    _game_id: int, _connection
) -> list[dict[int, str]]:
    cursor = _connection.cursor()
    SQL = "SELECT Description FROM Categories WHERE ID IN (SELECT Category_ID FROM `Game-Categories` WHERE Game_ID = ?)"
    cursor.execute(SQL, (_game_id,))
    results = []

    for result in cursor:
        results.append(result)

    return results


def get_game_genres(
    _game_id: int, _connection
) -> list[dict[int, str]]:
    cursor = _connection.cursor()
    SQL = "SELECT Description FROM Genres WHERE ID IN (SELECT Genre_ID FROM `Game-Genres` WHERE Game_ID = ?)"
    cursor.execute(SQL, (_game_id,))
    results = []

    for result in cursor:
        results.append(result)

    return results


if __name__ == "__main__":
    main()
