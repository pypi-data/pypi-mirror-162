# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import ddd

from ..subject import Subject


class SubjectRepository(ddd.Repository):
    __module__: str = 'libwebid.domain.repo'

    async def get(self, subject_id: int | None) -> Subject:
        raise NotImplementedError

    async def get_by_challenge_id(
        self,
        challenge_id: int
    ) -> Subject | None:
        raise NotImplementedError

    async def get_by_email(self, email: str) -> Subject | None:
        raise NotImplementedError

    async def persist(self, obj: Subject) -> Subject: # type: ignore
        raise NotImplementedError