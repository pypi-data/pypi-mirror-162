import logging
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from abotserver.providers.hikvision import acs_register

logger = logging.getLogger("gunicorn.access")

router = APIRouter()


class ACSConnection(BaseModel):
    url: str
    uri: str
    xcakey: str
    secret: str
    payload: dict


@router.post("/acs-register/")
async def register_acs(data: ACSConnection, tag: str = 'UNSET'):
    logger.info('Request Tag: {}'.format(tag))
    secret = data.secret
    if not secret:
        secret = "wZJkGrXo04vrtIiX30vx"
    try:
        response = acs_register(url=data.url,
                                uri=data.uri,
                                xcakey=data.xcakey,
                                secret=secret,
                                payload=data.payload)
    except Exception as exc:
        logger.error(str(exc))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=str(exc))
    if response:
        response = response.json()
    return response