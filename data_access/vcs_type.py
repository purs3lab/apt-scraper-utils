from . import BaseModel
from peewee import CharField


# Type of VCS. Specifically, github, debian.salsa, launchpad, svn
class VCSType(BaseModel):
    type_name = CharField(unique=True)

def setup_vcs_types() -> None:
    VCSType.get_or_create(type_name='github')
    VCSType.get_or_create(type_name='debian.salsa')
    VCSType.get_or_create(type_name='launchpad')
    VCSType.get_or_create(type_name='svn')
    VCSType.get_or_create(type_name='debian.git')
    VCSType.get_or_create(type_name='debian.anonscm')
    VCSType.get_or_create(type_name='debian.alioth')
    VCSType.get_or_create(type_name='custom.git')
    VCSType.get_or_create(type_name='unknown')

def get_vcs_type(vcs_url: str) -> VCSType:
    if "salsa.debian" in vcs_url:
        return VCSType.get(type_name='debian.salsa')
    elif "github.com" in vcs_url:
        return VCSType.get(type_name='github')
    elif "launchpad.net" in vcs_url:
        return VCSType.get(type_name='launchpad')
    elif "alioth.debian" in vcs_url:
        return VCSType.get(type_name='debian.alioth')
    elif "anonscm.debian" in vcs_url:
        return VCSType.get(type_name='debian.anonscm')
    elif "git.debian" in vcs_url:
        return VCSType.get(type_name='debian.git')
    elif "svn.debian" in vcs_url:
        return VCSType.get(type_name='svn')
    elif "git." in vcs_url:
        return VCSType.get(type_name='custom.git')
    else:
        return VCSType.get(type_name='unknown')