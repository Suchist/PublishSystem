#encoding:utf-8
from exts import db
from datetime import datetime

class User(db.Model):
    __tablename__='user'
    id = db.Column(db.String(100),primary_key=True)
    email = db.Column(db.String(20),nullable=False)

class Article(db.Model):
    __tablename__='article'
    id = db.Column(db.Integer,primary_key=True, autoincrement=True)

    title = db.Column(db.String(100),nullable=False)
    content = db.Column(db.Text, nullable=False)
    abstract = db.Column(db.String(100), nullable=False)
    highlight = db.Column(db.String(100), nullable=False)
    createTime = db.Column(db.DateTime, default=datetime.now())

    viewCount= db.Column(db.Integer)
    likeNumber = db.Column(db.Integer)
    unlikeNumber = db.Column(db.Integer)

    author_id=db.Column(db.String(100),db.ForeignKey('user.id'))
    subject_id = db.Column(db.Integer,db.ForeignKey('subject.id'))

    author = db.relationship('User',backref=db.backref('articles'))
    subject = db.relationship('Subject',backref=db.backref('articles'))

    def __init__(self,title,content,abstract,highlight,viewCount,likeNumber,unlikeNumber):
        self.title = title
        self.content = content
        self.abstract = abstract
        self.highlight = highlight
        self.viewCount = viewCount
        self.likeNumber = likeNumber
        self.unlikeNumber = unlikeNumber

    def findArticleById(article_id):
        article = Article.query.filter(Article.id == article_id).first()
        return article

class Comment(db.Model):
    __tablename__='comment'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    content = db.Column(db.Text, nullable=False)
    createTime = db.Column(db.DateTime, default=datetime.now())

    viewCount = db.Column(db.Integer)
    likeNumber = db.Column(db.Integer)
    unlikeNumber = db.Column(db.Integer)

    article_id = db.Column(db.Integer,db.ForeignKey('article.id'))
    author_id = db.Column(db.String(100), db.ForeignKey('user.id'))

    article = db.relationship('Article', backref=db.backref('comments'))
    author = db.relationship('User', backref=db.backref('comments'))

class Vote(db.Model):
    __tablename__='vote'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_ip = db.Column(db.Text, nullable=False)
    is_up = db.Column(db.Boolean)

    article_id = db.Column(db.Integer,db.ForeignKey('article.id'))
    article = db.relationship('Article', backref=db.backref('votes'))
    def to_json(self):
        dict = self.__dict__
        if "_sa_instance_state" in dict:
            del dict["_sa_instance_state"]
        return dict

    def __init__(self, id, user_ip, is_up, article_id):
        self.id = id
        self.user_ip = user_ip
        self.is_up = is_up
        self.article_id = article_id

class Subject(db.Model):
    __tablename__='subject'
    id = db.Column(db.Integer,primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)

class VoteComment(db.Model):
    __tablename__='vote_comment'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_ip = db.Column(db.Text, nullable=False)
    is_up = db.Column(db.Boolean)

    comment_id = db.Column(db.Integer,db.ForeignKey('comment.id'))

    def to_json(self):
        dict = self.__dict__
        if "_sa_instance_state" in dict:
            del dict["_sa_instance_state"]
        return dict

    def __init__(self, id, user_ip, is_up, comment_id):
        self.id = id
        self.user_ip = user_ip
        self.is_up = is_up
        self.comment_id = comment_id



