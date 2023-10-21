from . import BaseModel
from peewee import CharField


class SourceLanguage(BaseModel):
    language = CharField(unique=True)