#encoding:utf-8
#存放db
import pymysql
pymysql.install_as_MySQLdb()

from flask_sqlalchemy import SQLAlchemy
db=SQLAlchemy()
