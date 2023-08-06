# Copyright (C) 2022 Cochise Ruhulessin
# 
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Any

import fastapi

import pydantic
from cbra.conf import settings
from cbra.params import ServerCodec
from cbra.params import CurrentServer
from cbra.types import IPrincipal
from cbra.utils import current_timestamp
from ckms.jose import PayloadCodec


ACCEPTED_AUDIENCE: set[str] = getattr(settings, 'SESSION_AUDIENCE', None) or set()


class ISessionPrincipal(IPrincipal, pydantic.BaseModel):

    def get_session_id(self) -> int | None:
        raise NotImplementedError

    def set_session_id(self, id: int) -> None:
        raise NotImplementedError

    def is_established(self) -> bool:
        raise NotImplementedError


class NullSessionPrincipal(ISessionPrincipal):
    aud: set[str]
    id: int | None = None
    iat: int = pydantic.Field(default_factory=current_timestamp)
    iss: str

    def get_session_id(self) -> int | None:
        return self.id

    def is_authenticated(self) -> bool:
        return False

    def is_established(self) -> bool:
        return False

    def set_session_id(self, id: int) -> None:
        self.id = id


class UnauthenticatedSessionPrincipal(ISessionPrincipal):
    id: int | None = None
    aud: set[str]
    iat: int = pydantic.Field(default_factory=current_timestamp)
    iss: str

    def get_session_id(self) -> int | None:
        return self.id

    def is_authenticated(self) -> bool:
        return False

    def is_established(self) -> bool:
        return True

    def set_session_id(self, id: int) -> None:
        self.id = id


class AuthenticatedSessionPrincipal(ISessionPrincipal):
    aud: set[str]
    auth_time: int
    email: str
    email_verified: bool
    id: int
    iss: str
    sub: int
    mfa: int | None = None

    def get_session_id(self) -> int | None:
        return self.id

    def is_authenticated(self) -> bool:
        return True

    def is_established(self) -> bool:
        return True


class SessionPrincipal(ISessionPrincipal):
    __root__: AuthenticatedSessionPrincipal | UnauthenticatedSessionPrincipal

    @classmethod
    async def fromcookie(
        cls,
        codec: PayloadCodec = ServerCodec,
        issuer: str = CurrentServer,
        token: str = fastapi.Cookie(
            default=None,
            alias=settings.SESSION_COOKIE_NAME,
            title="Session",
            description=(
                "Identifies the current session associated to the user agent."
            )
        )
    ) -> ISessionPrincipal:
        audience = ACCEPTED_AUDIENCE or {issuer}
        if token is None:
            return NullSessionPrincipal(aud=audience, iss=issuer)
        try:
            _, claims = await codec.jwt(
                token=str.encode(token, 'ascii'),
                accept="jwt+session"
            )
            claims.verify(
                audience=ACCEPTED_AUDIENCE or {issuer}
            )
            principal = cls.parse_obj({
                'aud': audience,
                'iss': issuer,
                **claims.dict()
            })
        except Exception:
            principal = NullSessionPrincipal(aud=audience, iss=issuer)
        return principal

    @classmethod
    def parse_obj(cls, obj: Any) -> ISessionPrincipal:
        return super().parse_obj(obj).__root__