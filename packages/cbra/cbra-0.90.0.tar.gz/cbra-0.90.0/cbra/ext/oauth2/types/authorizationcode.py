"""Declares :class:`AuthorizationCode`."""
import datetime

import pydantic


class AuthorizationCode(pydantic.BaseModel):
    __module__: str = 'cbra.ext.oauth2.types'
    created: datetime.datetime = pydantic.Field(
        default_factory=datetime.datetime.utcnow
    )

    code: str

    request_id: str