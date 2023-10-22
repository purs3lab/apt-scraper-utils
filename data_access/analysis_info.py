from . import BaseModel
from peewee import CharField, ForeignKeyField
from .pkg import DebianPackage

class CodeQLInfo(BaseModel):
    sarif_path = CharField(unique=True, null=True)
    codeql_db_path = CharField(unique=True, null=True)
    pkg = ForeignKeyField(DebianPackage, backref='codeqlresult')
