#!/usr/bin/env python
# -*- coding:utf-8 -*-

import json
import platform
import ssl
import traceback
import urllib
from urllib import request

from hsbind import rsa_utils
from hsbind.common_utils import get_logger

logging = get_logger(__name__)

test_http_domain = "https://openapi-daily.hstong.com"
prod_http_domain = "https://openapi.hstong.com"

send_auth_code_path = "/hs/devicebind/sendAuthCode"
send_bing_request_path = "/hs/devicebind/bind"


def send_auth_code(env, country_code, mobile, key):
    if len(env) == 0 or len(country_code) == 0 or len(mobile) == 0 or len(key) == 0:
        logging.error(f"send auth code error, param is invalid.")
        return None, None

    url = ""
    if env == "1":
        url = test_http_domain + send_auth_code_path
    elif env == "2":
        url = prod_http_domain + send_auth_code_path

    if len(url) == 0:
        logging.error(f"send auth code error, request url is null.")
        return None, None

    try:
        sign_bytes = rsa_utils.rsa_sign(mobile, key)
        sign = sign_bytes.hex()

        data = {
            "countryCode": country_code,
            "mobile": mobile,
            "sign": sign,
        }
        headers = {'Content-Disposition': 'form-data', 'Accept-Charset': 'utf-8',
                   'Content-Type': 'application/x-www-form-urlencoded'}

        data = urllib.parse.urlencode(data).encode("utf-8")
        req = request.Request(url=url, data=data, headers=headers, method='POST')
        with request.urlopen(req, context=ssl._create_unverified_context()) as resp:
            response = resp.read()

        response = json.loads(rsa_utils.bytes_to_str(response))
        return response.get("respCode"), response.get("respMsg")
    except Exception as e:
        logging.error(traceback.print_exc())
    return None, None


def send_bind_request(env, country_code, mobile, key, code, device_no):
    if len(env) == 0 or len(country_code) == 0 or len(mobile) == 0 or len(key) == 0 or len(code) == 0:
        logging.error(f"send bind request error, param is invalid.")
        return None, None

    url = ""
    if env == "1":
        url = test_http_domain + send_bing_request_path
    elif env == "2":
        url = prod_http_domain + send_bing_request_path

    if len(url) == 0:
        logging.error(f"send bind request error, request url is null.")
        return None, None

    try:
        sign_bytes = rsa_utils.rsa_sign(mobile, key)
        sign = sign_bytes.hex()
        
        data = {
            "code": code,
            "countryCode": country_code,
            "mobile": mobile,
            "deviceNo": device_no,
            "deviceType": platform.platform(),
            "deviceName": "open-api",
            "sign": sign,
        }
        headers = {'Content-Disposition': 'form-data', 'Accept-Charset': 'utf-8',
                   'Content-Type': 'application/x-www-form-urlencoded'}

        data = urllib.parse.urlencode(data).encode("utf-8")
        req = request.Request(url=url, data=data, headers=headers, method='POST')
        with request.urlopen(req, context=ssl._create_unverified_context()) as resp:
            response = resp.read()

        response = json.loads(rsa_utils.bytes_to_str(response))
        return response.get("respCode"), response.get("respMsg")
    except Exception as e:
        logging.error(traceback.print_exc())
    return None, None
