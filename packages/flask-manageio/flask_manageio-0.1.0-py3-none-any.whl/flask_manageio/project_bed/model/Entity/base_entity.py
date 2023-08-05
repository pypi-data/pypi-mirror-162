from datetime import datetime
from typing import Union, List
from sqlalchemy import Column, Integer, DateTime

from db import db


def create_tables(app_, db_):
    with app_.app_context():
        db_.create_all()


class BaseEntity(db.Model):
    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    @classmethod
    def find_by_id(cls, _id: Union[int, str]) -> db.Model:
        return cls.query.filter_by(id=_id).first()

    @classmethod
    def find_all(cls) -> List[db.Model]:
        return cls.query.all()

    @classmethod
    def find_by(cls, _column: db.Column, data: Union[int, str]) -> db.Model:
        return cls.query.filter_by(_column=data).first()

    @classmethod
    def raw_sql(cls, sql: str):
        return db.session.execute(sql)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
