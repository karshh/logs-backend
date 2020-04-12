from .db import db

class Action(db.EmbeddedDocument):
    _time = db.StringField(db_field='time', required=True)
    _type = db.StringField(db_field='type', required=True)
    _properties = db.DictField(db_field='properties', required=True)