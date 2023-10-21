from . import BaseModel
from peewee import CharField


class PkgCategory(BaseModel):
    category_name = CharField(unique=True)