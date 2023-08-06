import os
import hashlib
import requests
import json

JIESHUN_DIR = os.path.join(os.environ['HOME'], 'jieshun')
JIESHUN_TOKEN_PATH = os.path.join(JIESHUN_DIR, 'token')


def store_token(token):
    if not os.path.exists(JIESHUN_DIR):
        os.mkdir(JIESHUN_DIR)

    with open(JIESHUN_TOKEN_PATH, mode='w+') as f:
        f.writelines(token)


def get_exist_token():
    if not os.path.exists(JIESHUN_DIR):
        return None

    with open(JIESHUN_TOKEN_PATH, mode='r+') as f:
        return f.read()


def fetch_token(server_url, cno, usr, psw):
    login_url = server_url + "login"
    payload = {
        "cno": cno,
        "usr": usr,
        "psw": psw
    }
    headers = {
        "Content-Type": "application/json",
    }
    req = requests.post(login_url, headers=headers, data=json.dumps(payload)).json()
    return req.get("token", None) if req else None


def call_jsst(server_url, postfix_url, seq_id, cno, usr, psw, sign_key, p):
    token = get_exist_token()
    if not token:
        token = (fetch_token(server_url=server_url, cno=cno, usr=usr, psw=psw))
        store_token(token)
    data = {
        "cno": cno,
        "tn": token,
        "p": p,
        "seqId": seq_id
    }
    url = server_url + postfix_url
    content = json.dumps(data) + sign_key
    sn = hashlib.md5(content.encode('UTF-8')).hexdigest()
    headers = {
        "Content-Type": "application/json",
        "sn": sn,
    }
    try:
        req = requests.post(url, data=json.dumps(data), headers=headers)
        return req.json()
    except Exception:
        token = (fetch_token(server_url=server_url, cno=cno, usr=usr, psw=psw))
        store_token(token)
