import configparser
import hashlib
import logging
import os
from typing import Dict, NoReturn
import argparse

import psycopg2
from dotenv import load_dotenv


class Configuration:
    CONFIG: configparser.ConfigParser = None
    CONFIGURATION_FILE = "config.ini"

    @staticmethod
    def set_up():
        if Configuration.CONFIG is None:
            Configuration.__instantiate__()
        return Configuration.CONFIG

    @staticmethod
    def __instantiate__():
        Configuration.CONFIG = configparser.ConfigParser()
        Configuration.CONFIG.read(Configuration.CONFIGURATION_FILE)

    @staticmethod
    def get(option: str, section: str = 'DATABASE') -> str | None:
        Configuration.set_up()
        return Configuration.CONFIG.get(section=section, option=option, vars=os.environ)


def get_config_for_db() -> Dict[str, str] | None:
    dbname = Configuration.get('DB_NAME')
    user = Configuration.get('DB_USER')
    password = Configuration.get('DB_PASS')
    host = Configuration.get('DB_HOST')
    port = Configuration.get('DB_PORT')
    if all([dbname, user, password, host, port]):
        return {
            'dbname': dbname,
            'user': user,
            'password': password,
            'host': host,
            'port': port
        }
    return None


def create_db(config: Dict[str, str]):
    logging.debug("Connecting to the postgresql db 🐘")
    try:
        return psycopg2.connect(**config)
    except Exception as e:
        logging.error(f"Error al conectar a la base de datos: {e}")
        return None


def create_tables(conn):
    cursor = conn.cursor()
    logging.debug("Creating refuge table.... 🕝")
    create_refugios_table_query = """
    CREATE TABLE IF NOT EXISTS refugios (
        id_refugio VARCHAR(255) PRIMARY KEY,
        password_hash VARCHAR(255) NOT NULL
    );
    """
    cursor.execute(create_refugios_table_query)

    logging.debug("Creating events table.... 🕝")
    create_eventos_table_query = """
    CREATE TABLE IF NOT EXISTS eventos (
        id SERIAL PRIMARY KEY,
        timestamp TIMESTAMP NOT NULL,
        id_refugio VARCHAR(255) NOT NULL,
        people_in INT,
        people_out INT,
        eventos INT,
        FOREIGN KEY (id_refugio) REFERENCES refugios(id_refugio)
    );
    """
    cursor.execute(create_eventos_table_query)

    logging.debug("Writting changes to the database... ✍")
    conn.commit()
    cursor.close()
    logging.info("Database configuration done! 🚀")


def get_db_config() -> Dict[str, str] | NoReturn:
    config: Dict[str, str] | None = get_config_for_db()
    if config is None:
        logging.info("Database configuration failing 🔴, exiting.. ")
        exit(-1)
    return config


def get_db(config: Dict[str, str]) -> any | NoReturn:
    db = create_db(config=config)
    if db is None:
        logging.info("Database connection failing 🔴, exiting.. ")
        exit(-1)
    return db


def load_environment_vars_if_debug_mode():
    parser = argparse.ArgumentParser(description='Database configuration')
    parser.add_argument('--debug', action='store_true', default=False, help='Debug mode')
    args = parser.parse_args()
    if args.debug:
        load_dotenv()


def populate_db(db):
    cursor = db.cursor()
    logging.debug("Adding refuges....🏠")
    refuge_id = Configuration.get(option='REFUGE_ID', section='POPULATE_DB')
    password = Configuration.get(option='REFUGE_PASSWORD', section='POPULATE_DB')
    password_hashed = hashlib.sha256(password.encode()).hexdigest()
    cursor.execute("INSERT INTO refugios (id_refugio, password_hash) VALUES (%s, %s)", (refuge_id, password_hashed))
    db.commit()
    cursor.close()


def main():
    load_environment_vars_if_debug_mode()
    config = get_db_config()
    db = get_db(config=config)
    create_tables(db)
    populate_db(db)
    db.close()


if __name__ == '__main__':
    main()
