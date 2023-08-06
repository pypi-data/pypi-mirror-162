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

from ckms.core import Keychain
from ckms.jose import PayloadCodec
from ckms.types import JSONWebKeySet

from .iresponsehandler import IResponseHandler


class Request(fastapi.Request):

    @property
    def codec(self) -> PayloadCodec:
        """The :class:`~ckms.jose.PayloadCodec` instance used to
        decode JOSE objects.
        """
        return self.app.codec

    @property
    def keychain(self) -> Keychain:
        """The :class:`~ckms.core.Keychain` instance holding the
        signing and decryption keys used by the application.
        """
        return self.app.keychain

    @property
    def jwks(self) -> JSONWebKeySet:
        """A :class:`~ckms.types.JSONWebKeySet` holding the public keys intended
        for external consumers.
        """
        return self.keychain.tagged('unimatrixone.io/public-keys').as_jwks()

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.response_handlers = []

    def add_response_handler(self, handler: IResponseHandler):
        if 'handlers' not in self.scope:
            self.scope['handlers'] = []
        self.scope['handlers'].append(handler)

    async def run_response_handlers(
        self,
        response: fastapi.Response
    ) -> fastapi.Response | None:
        """Run all response handlers that are registered for this
        request.
        """
        for handler in self.response_handlers:
            result = await handler.on_response(self, response)
            if result is not None:
                response = result
                break
        return response

