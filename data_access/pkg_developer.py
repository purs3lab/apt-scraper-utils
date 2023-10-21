from . import BaseModel
from peewee import CharField, ForeignKeyField


# list, ind_debian, ind_custom
class ContactType(BaseModel):
    typename = CharField(unique=True)

class DeveloperContact(BaseModel):
    email = CharField(unique=True)
    type = ForeignKeyField(ContactType, backref='contacts')