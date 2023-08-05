class Config:
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "postgresql://develop:root123@localhost/bidservice"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = "change-this-key-in-the-application-config"
    JWT_SECRET_KEY = "change-this-key-to-something-different-in-the-application-config"
