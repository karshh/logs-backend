from .db import db


class ClickProperties(db.EmbeddedDocument):
    locationX = db.IntField(required=True)
    locationY = db.IntField(required=True)

class ViewProperties(db.EmbeddedDocument):
    viewedId = db.StringField(required=True)

class NavigateProperties(db.EmbeddedDocument):
    pageFrom = db.StringField(required=True)
    pageTo = db.StringField(required=True)