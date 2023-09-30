"""Read environment variables and construct the connection string for MySQL DB"""
import pandas as pd

# import all DDL classes
from models import *

from dotenv import dotenv_values
from dotenv import load_dotenv

from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session
from pandas import DataFrame

from typing import Tuple


class DbService:
    session_entries: int = 0
    rate_limit: bool = False

    def __init__(self):
        self.engine: Engine = create_engine(self.conn_string())
        self.session: Session = self.create_session()

    def conn_string(self) -> str:
        env = dotenv_values(".env")
        # env = load_dotenv()
        print(env)

        return "mysql+pymysql://%s:%s@%s/%s" % (
            env["DB_USER"],
            env["DB_PASSWORD"],
            env["DB_HOST"],
            env["DB_NAME"],
        )

    def create_session(self) -> Session:
        Base.metadata.create_all(bind=self.engine)

        Session = sessionmaker(bind=self.engine)
        return Session()

    def refresh(self) -> None:
        Base.metadata.reflect(bind=self.engine)
        Base.metadata.drop_all(bind=self.engine)

        Base.metadata.create_all(bind=self.engine)

        self.session.commit()

    def add_entry(self, orm_model_entry) -> None:
        self.session.add(orm_model_entry)
        self.session.commit()

    def query(self, orm_model, num_entries: int) -> DataFrame:
        with self.engine.connect() as conn:
            return pd.read_sql_query(
                sql=self.session.query(orm_model).limit(num_entries).statement,
                con=conn,
            )

    def latest(self, orm_model) -> DataFrame:
        with self.engine.connect() as conn:
            return self.session.query(orm_model).order_by(orm_model.id.desc()).first()

    def clear_table(self, orm_model) -> None:
        self.session.query(orm_model).delete()
        self.session.commit()
