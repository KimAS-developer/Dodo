class Config_db(object):
    SQLALCHEMY_DATABASE_URI = f'postgresql://postgres:root@localhost:5432/dodo'
    SECRET_KEY = 'ASJDJhfkjahwoi123'
    SQLALCHEMY_TRACK_MODIFICATIONS = True
