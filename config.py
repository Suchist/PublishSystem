#encoding:utf-8
import os

DEBUG=True
SECRET_KEY=os.urandom(24)

#DB_URI = "mysql+mysqldb://root:123456@localhost:3306/publishsystem?charset=utf8"
DB_URI = "sqlite:///publishsystem.db"
SQLALCHEMY_DATABASE_URI = DB_URI
SQLALCHEMY_TRACK_MODIFICATIONS = False


