# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Any

import pydantic


class SessionAssertion(pydantic.BaseModel):
    auth_time: int
    aal: int = 1
    ial: int = 1
    allow_mfa_registration: bool = False
    challenge_id: int
    email: pydantic.EmailStr | None = None
    email_verified: bool = False
    sub: int | None = None

    def dict(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        kwargs.setdefault('exclude_none', True)
        return super().dict(*args, **kwargs)

