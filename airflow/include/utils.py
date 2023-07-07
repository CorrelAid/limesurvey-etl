import sys

from sqlalchemy import create_engine


def connect_to_mariadb(
    db_host: str, db_port: int, db_user: str, db_password: str, db_name: str
):
    """
    Connects to a MariaDB database and returns a SQLAlchemy engine.
    :param db_host: Host of the database.
    :param db_port: Port of the database.
    :param db_user: Name of the database user.
    :param db_password: Password to authenticate the database user.
    :param db_name: Name of the database to connect with.
    :return: A SQLAlchemy engine.
    :rtype: sqlalchemy.engine.Engine
    """
    try:
        print("Connecting to MariaDB")
        url = (
            f"mariadb+mariadbconnector://{db_user}"
            f":{db_password}"
            f"@{db_host}"
            f":{db_port}"
            f"/{db_name}"
        )
        engine = create_engine(url, echo=True)
        print("Connection to MariaDB established")

        return engine
    except exc.SQLAlchemyError as e:
        print(f"Error connecting to MariaDB: {e}")
        sys.exit(1)
