import logging
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from abotserver.providers.jsst import call_jsst

logger = logging.getLogger("gunicorn.access")

router = APIRouter()


class JSSTData(BaseModel):
    server_url: str
    postfix_url: str
    seq_id: str
    cno: str
    usr: str
    psw: str
    sign_key: str
    p: dict


@router.post("/call-jsst/")
async def register_acs(data: JSSTData, tag: str = 'UNSET'):
    logger.info('Request Tag: {}'.format(tag))
    try:
        response = call_jsst(server_url=data.server_url,
                             postfix_url=data.postfix_url,
                             seq_id=data.seq_id,
                             cno=data.cno,
                             usr=data.usr,
                             psw=data.psw,
                             sign_key=data.sign_key,
                             p=data.p)
    except Exception as exc:
        logger.error(str(exc))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=str(exc))
    return response
