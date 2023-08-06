import logging
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from abotserver.providers.aliyun import call_aliyun_nlp

logger = logging.getLogger("gunicorn.access")

router = APIRouter()


class AliyunNLP(BaseModel):
    access_key_id: str
    access_key_secret: str
    endpoint: str
    api_version: str
    region_id: str
    model_id: str
    model_version: str
    content: str


@router.post("/aliyun-nlp-service/")
async def call_aliyun_nlp_service(data: AliyunNLP, tag: str = 'UNSET'):
    try:
        logger.info('Request Tag: {}'.format(tag))
        response = call_aliyun_nlp(access_key_id=data.access_key_id,
                                   access_key_secret=data.access_key_secret,
                                   endpoint=data.endpoint,
                                   api_version=data.api_version,
                                   region_id=data.region_id,
                                   model_id=data.model_id,
                                   model_version=data.model_version,
                                   content=data.content)
    except Exception as exc:
        logger.error(str(exc))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=str(exc))

    return response if response else None

