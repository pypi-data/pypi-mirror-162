# Copyright (C) 2022 Cochise Ruhulessin
# 
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import pydantic
from unimatrix.lib import timezone


class Subject(pydantic.BaseModel):
    id: int | None = None
    challenge_id: int
    created: int = pydantic.Field(default_factory=timezone.now)
    primary_email: pydantic.EmailStr

    #: The Level of Assurance (LoA) with regards to the asserted identity.
    #:
    ial: int = 1
