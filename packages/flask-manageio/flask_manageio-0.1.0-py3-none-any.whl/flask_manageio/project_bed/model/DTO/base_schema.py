from ma import ma


class BaseSchema(ma.SQLAlchemyAutoSchema):
    __abstract__ = True
