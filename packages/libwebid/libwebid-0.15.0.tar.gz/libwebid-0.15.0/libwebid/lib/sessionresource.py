# Copyright (C) 2022 Cochise Ruhulessin
# 
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Any

from cbra.params import ServerCodec
from cbra.resource import Resource
from ckms.jose import PayloadCodec

from .principal import ISessionPrincipal
from .principal import SessionPrincipal
from .sessionresponsehandler import SessionResponseHandler


class SessionResource(Resource):
    __abstract__: bool = True
    codec: PayloadCodec = ServerCodec
    dirty: bool = False
    principal: ISessionPrincipal
    principal_factory: Any = SessionPrincipal.fromcookie
    session_required: bool = False

    def persist_session_cookie(
        self,
        session: ISessionPrincipal
    ) -> None:
        self.dirty = True
        self.request.add_response_handler(
            SessionResponseHandler(codec=self.codec, principal=session)
        )