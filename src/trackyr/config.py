import os
import json

with open('/etc/trackyr-config.json') as config_file:
    config = json.load(config_file)

class Config:
    SECRET_KEY = config.get('SECRET_KEY')

    POSTGRES_URL = config.get('POSTGRES_URL')
    POSTGRES_USER = config.get('POSTGRES_USER')
    POSTGRES_PW = config.get('POSTGRES_PW')
    POSTGRES_DB = config.get('POSTGRES_DB')

    SQLALCHEMY_DATABASE_URI = f"postgresql://{POSTGRES_USER}:{POSTGRES_PW}@{POSTGRES_URL}/{POSTGRES_DB}"
