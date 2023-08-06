# Copyright (C) 2022 Cochise Ruhulessin
# 
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import fastapi

from cbra.conf import settings
from cbra.types import IResponseHandler
from ckms.jose import PayloadCodec

from .principal import ISessionPrincipal


class SessionResponseHandler(IResponseHandler):
    codec: PayloadCodec
    domain: str | None
    path: str = '/'
    principal: ISessionPrincipal
    samesite: str = 'strict'
    token_type: str = "jwt+session"

    def __init__(
        self,
        *,
        codec: PayloadCodec,
        principal: ISessionPrincipal,
        domain: str | None = None
    ):
        self.codec = codec
        self.domain = domain
        self.principal = principal

    async def on_response(
        self,
        request: fastapi.Request,
        response: fastapi.Response
    ) -> None:
        payload = self.principal.dict()
        token = await self.codec.encode(
            payload=payload,
            signers=[settings.SESSION_SIGNER],
            encrypters=[settings.SESSION_ENCRYPTER],
            allow_compact=True,
            allow_flattened=True,
            content_type=self.token_type
        )
        response.set_cookie(
            key=settings.SESSION_COOKIE_NAME,
            value=token,
            max_age=86000 * 365,
            secure=True,
            httponly=True,
            samesite=self.samesite,
            domain=self.domain,
            path=self.path
        )