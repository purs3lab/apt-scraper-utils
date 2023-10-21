from . import BaseModel
from peewee import CharField


# Type of VCS. Specifically, github, debian.salsa, launchpad, svn
class VCSType(BaseModel):
    type_name = CharField(unique=True)