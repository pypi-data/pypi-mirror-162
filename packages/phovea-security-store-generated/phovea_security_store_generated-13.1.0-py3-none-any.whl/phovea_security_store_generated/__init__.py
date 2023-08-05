#####################################################################
# Copyright (c) The Caleydo Team, http://caleydo.org
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#####################################################################


from typing import Type

from pydantic import BaseModel
from tdp_core.plugin.model import AVisynPlugin, RegHelper

from .settings import PhoveaSecurityStoreGeneratedSettings


class VisynPlugin(AVisynPlugin):
    def register(self, registry: RegHelper):
        registry.append(
            "namespace",
            "phovea_security_store_generated_api",
            "phovea_security_store_generated.api",
            {"namespace": "/api/tdp/security_store_generated"},
        )

        registry.append("user_stores", "phovea_security_store_generated_store", "phovea_security_store_generated.store", {})

    @property
    def setting_class(self) -> Type[BaseModel]:
        return PhoveaSecurityStoreGeneratedSettings
