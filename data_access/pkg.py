from . import BaseModel
from peewee import CharField, FloatField, BooleanField, ForeignKeyField
from pkg_language import SourceLanguage
from pkg_category import PkgCategory
from pkg_developer import DeveloperContact
from vcs_type import VCSType

class DebianPackage(BaseModel):
    name = CharField(unique=True)
    language = ForeignKeyField(SourceLanguage, backref='pkgs')
    category = ForeignKeyField(PkgCategory, backref='pkgs')
    size_sloc_kb = FloatField(default=0.0)
    has_src = BooleanField(default=True)
    src_download_url = CharField(default=None, null=True)
    dsc_download_url = CharField(default=None, null=True)
    deb_download_url = CharField(default=None, null=True)

class VCSInfo(BaseModel):
    pkg = ForeignKeyField(DebianPackage, backref='vcs')
    vcs_url = CharField()
    vcs_type = ForeignKeyField(VCSType, backref='pkgs')
    class Meta:
        indexes = (
            # Specify a unique multi-column index on from/to-user.
            (('pkg', 'vcs_url', 'vcs_type'), True),
        )

class PkgDevelopers(BaseModel):
    pkg = ForeignKeyField(DebianPackage, backref='developers')
    developer = ForeignKeyField(DeveloperContact, backref='pkgs')
    class Meta:
        indexes = (
            # Specify a unique multi-column index on from/to-user.
            (('pkg', 'developer'), True),
        )