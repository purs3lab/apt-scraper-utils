from . import BaseModel
from peewee import CharField, ForeignKeyField


# list, ind_debian, ind_custom
class ContactType(BaseModel):
    typename = CharField(unique=True)

class DeveloperContact(BaseModel):
    email = CharField(unique=True)
    type = ForeignKeyField(ContactType, backref='contacts')

def setup_contact_types() -> None:
    ContactType.get_or_create(typename='list')
    ContactType.get_or_create(typename='debian')
    ContactType.get_or_create(typename='custom')

def get_developer_contact(dev_email: str) -> DeveloperContact:
    if "@lists" in dev_email:
        return DeveloperContact.get_or_create(email=dev_email, type=ContactType.get(typename='list'))
    elif "@debian" in dev_email:
        return DeveloperContact.get_or_create(email=dev_email, type=ContactType.get(typename='debian'))
    else:
        return DeveloperContact.get_or_create(email=dev_email, type=ContactType.get(typename='custom'))