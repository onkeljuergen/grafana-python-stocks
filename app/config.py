import os
import secrets
from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from dataclasses import dataclass



class EnvironConfig:
    stocks_db = os.environ['STOCKS_DB']
    stocks_db_host = os.environ['STOCKS_DB_HOST']
    stocks_db_user = os.environ['STOCKS_DB_USER']
    stocks_db_pwd = os.environ['STOCKS_DB_PWD']
    influx_host = os.environ['INFLUXDB_HOST']
    influx_port = os.environ['INFLUXDB_PORT']
    influx_db = os.environ['INFLUXDB_DB']

    secret = secrets.token_urlsafe(32)

def get_db_connection():
    connection = f'sqlite:///{EnvironConfig.stocks_db}' \
        if EnvironConfig.stocks_db \
        else f'postgresql://{EnvironConfig.stocks_db_user}:{EnvironConfig.stocks_db_pwd}@{EnvironConfig.stocks_db_host}:5432/stocks'

    print('Connect to: {}'.format(connection))
    return connection


class Config(object):
    JOBS=[
        {
            'id': 'update_influxdb',
            'func': 'task:update_influxdb_task',
            'args': (),
            'trigger': 'interval',
            'seconds': 60
        }
    ]

    SCHEDULER_API_ENABLED = True
    SQLALCHEMY_DATABASE_URI = get_db_connection()
    SECRET_KEY = EnvironConfig.secret

app = Flask(__name__)
app.config.from_object(Config())
app.url_map.strict_slashes = False

api = Api(app)

db = SQLAlchemy(app)