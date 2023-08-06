import json
from aliyunsdkcore.client import AcsClient
from aliyunsdknlp_automl.request.v20191111 import GetPredictResultRequest


def call_aliyun_nlp(access_key_id, access_key_secret, endpoint, api_version,
                    region_id, model_id, model_version, content):

    client = AcsClient(access_key_id, access_key_secret, region_id)
    request = GetPredictResultRequest.GetPredictResultRequest()

    request.set_ModelId(model_id)
    request.set_ModelVersion(model_version)
    request.set_endpoint(endpoint)
    request.set_version(api_version)
    request.set_Content(content)
    response = client.do_action_with_exception(request)
    return json.loads(response)