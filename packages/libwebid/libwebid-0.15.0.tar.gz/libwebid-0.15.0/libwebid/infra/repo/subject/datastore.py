# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from libwebid import domain
from libwebid.lib.repo.googledatastore import GoogleDatastoreRepository


class DatastoreSubjectRepository( # type: ignore
    domain.SubjectRepository,
    GoogleDatastoreRepository
):
    kind: str = 'Subject'
    id_attr: str = 'id'

    async def get_by_challenge_id(
        self,
        challenge_id: int
    ) -> domain.Subject | None:
        query = self.query()
        query.add_filter('challenge_id', '=', challenge_id) # type: ignore
        return await self.first(query)

    async def get_by_email(
        self,
        email: str
    ) -> domain.Subject | None:
        query = self.query()
        query.add_filter('primary_email', '=', email) # type: ignore
        return await self.first(query)

    async def persist( # type: ignore
        self,
        obj: domain.Subject
    ) -> domain.Subject:
        return await self.persist_model(obj) # type: ignore