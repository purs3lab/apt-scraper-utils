from . import BaseModel
from peewee import CharField, ForeignKeyField, BooleanField
from .pkg import DebianPackage

class CodeQLInfo(BaseModel):
    sarif_path = CharField(unique=True, null=True)
    codeql_db_path = CharField(unique=True, null=True)
    is_manually_analyzed = BooleanField(default=False)
    codeql_failed_reason = CharField(default=None, null=True)
    pkg = ForeignKeyField(DebianPackage, backref='codeqlresult')
