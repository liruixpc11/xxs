# coding=UTF-8

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


Base = declarative_base()
DB_FILE = '/var/lib/cadts/xxs/xxs.db'
DEFAULT_CONNECTION_URL = 'sqlite:///' + DB_FILE


class SessionWrapper:
    def __init__(self, session):
        self.session = session

    def __enter__(self):
        return self.session

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_val:
            self.session.rollback()
        else:
            self.session.commit()
        self.session.close()


class DbFactory:
    def __init__(self, connection_url=DEFAULT_CONNECTION_URL):
        self.connection_url = connection_url
        self.engine = create_engine(connection_url)
        self.make_session = sessionmaker(bind=self.engine)

    def init_schema(self):
        if self.connection_url.endswith(DB_FILE):
            dirname = os.path.dirname(DB_FILE)
            if not os.path.isdir(dirname):
                os.makedirs(dirname)
        Base.metadata.create_all(self.engine)

    def create_connection(self):
        return self.engine.connect()

    def create_session(self, **kwargs):
        return SessionWrapper(self.make_session(**kwargs))
