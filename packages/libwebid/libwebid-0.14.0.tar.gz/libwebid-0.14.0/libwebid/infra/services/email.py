# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
"""Declares :class:`EmailService`."""
import asyncio
import logging
import os
from typing import cast
from typing import Any

import sendgrid
from sendgrid.helpers.mail import Content
from sendgrid.helpers.mail import Email
from sendgrid.helpers.mail import Mail
from sendgrid.helpers.mail import Subject
from sendgrid.helpers.mail import To
from unimatrix.exceptions import CanonicalException


class EmailService:
    """Declares an interface to send emails using SendGrid."""
    logger = logging.getLogger('unimatrix')

    class EmailServiceNotAvailable(CanonicalException):
        code = 'SERVICE_NOT_AVAILABLE'
        http_status_code = 503
        message = "The email service is currently not available."
        detail = "We contacted the email server but did not succeed."
        hint = (
            "If the problem persist, please contact customer support or "
            "a system administrator."
        )

    @property
    def client(self) -> sendgrid.SendGridAPIClient:
        c =  sendgrid.SendGridAPIClient(
            api_key=self.sendgrid_api_key)
        c.client.timeout = 10 # type: ignore
        return c

    @property
    def sendgrid_api_key(self) -> str:
        if not os.getenv('SENDGRID_API_KEY'):
            raise self.EmailServiceNotAvailable
        return cast(str, os.getenv('SENDGRID_API_KEY'))

    def get_sender(self, realm: str) -> str:
        """Return a string holding the email address that is used a
        a sender.
        """
        return f'noreply@webidentity.id'

    async def send_realm(self, realm: str, *args: Any, **kwargs: Any) -> bool:
        return await self.send(self.get_sender(realm), *args, **kwargs)

    async def send(self,
        sender: str,
        recipients: list[str],
        subject: str,
        text: str | None,
        html: str | None
    ) -> bool:
        """Send an email using the given parameters."""
        msg = Mail()
        msg.to = [To(x) for x in recipients]
        msg.from_email = Email(sender)
        msg.subject = Subject(subject)
        content: list[Content] = []
        if text is not None:
            content.append(Content('text/plain', text))
        if html is not None:
            content.append(Content('text/html', html))
        msg.content = content
        return await self._send(msg)

    async def _send(self, msg: Mail) -> bool:
        loop = asyncio.get_running_loop()
        f = self.client.send # type: ignore
        try:
            response = await loop.run_in_executor( # type: ignore
                None, lambda: f(msg)) # type: ignore
        except Exception as e: # pylint: disable=broad-except
            if not hasattr(e, 'status_code'):
                self.logger.error("Failed to send email caused by %s", e)
                return False
            response = e
            self.logger.exception(
                "Failed to send email (response: %s)",
                response.status_code # type: ignore
            )
        if response.status_code >= 400: # type: ignore
            return False

        return True
