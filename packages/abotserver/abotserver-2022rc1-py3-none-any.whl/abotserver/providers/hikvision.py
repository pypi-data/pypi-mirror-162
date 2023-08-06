import json
import datetime
import requests
import hmac
import base64
from hashlib import sha256


def signature_generating(method='POST',
                         content_type="application/json",
                         date=None,
                         xcakey="29836964",
                         secret=None,
                         uri="/artemis/api/visitor/v1/orderless/register"):
    content = "{}\n*/*\n{}\n{}\nx-ca-key:{}\n{}".format(method, content_type, date, xcakey, uri)
    signature = base64.b64encode(hmac.new(secret.encode('utf8'),
                                          content.encode('utf8'),
                                          digestmod=sha256).digest())
    return signature


def acs_register(url, uri, xcakey, payload, secret):
    content_type = "application/json"
    date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    headers = {
        "Accept": "*/*",
        "Content-Type": content_type,
        "Date": date,
        "x-Ca-Key": xcakey,
        "X-Ca-Signature": signature_generating(date=date,
                                               secret=secret,
                                               uri=uri),
        "X-Ca-Signature-Headers": "x-ca-key"
    }
    return requests.post(url=url, headers=headers, data=json.dumps(payload), verify=False)
