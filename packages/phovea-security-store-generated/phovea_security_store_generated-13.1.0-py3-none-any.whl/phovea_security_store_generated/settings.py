from pydantic import BaseModel
from tdp_core import manager


class PhoveaSecurityStoreGeneratedSettings(BaseModel):
    # TODO: Have a global datadir settings in tdp_core and extend it here.
    file: str = "./fakeUsers.db"


def get_settings() -> PhoveaSecurityStoreGeneratedSettings:
    return manager.settings.phovea_security_store_generated
