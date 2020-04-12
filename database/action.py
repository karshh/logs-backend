from .db import db
from database.properties import ClickProperties, NavigateProperties, ViewProperties
from enum import Enum 

class Action(db.EmbeddedDocument):
    _time = db.StringField(db_field='time',required=True)
    _properties = db.GenericEmbeddedDocumentField(db_field='properties',choices=[ClickProperties, NavigateProperties, ViewProperties])
    _type = db.StringField(db_field='type', choices=['CLICK', 'NAVIGATE', 'VIEW'], required=True)