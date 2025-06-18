from . import db

class User(db.Model):
    __bind_key__ = 'ndc-users'
    #id = db.Column(
    #email = db.Column(db.String(254), 
