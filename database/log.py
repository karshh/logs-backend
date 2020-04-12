from .db import db
from .action import Action

class Log(db.Document):
    userId = db.StringField(required=True)
    sessionId = db.StringField(required=True)
    actions = db.ListField(db.EmbeddedDocumentField(Action), required=True)