#!/usr/bin/env python
# -*- coding:utf-8 -*-

import traceback

from hsbind import network_request, network_utils
from hsbind.common_utils import get_logger
from hsbind.mobile_validator import is_mobile

logging = get_logger(__name__)


def bind():
    env = "1"
    country_code = ""
    mobile = ""
    key = ""

    for i in range(4):
        env = input("请选择连接环境(1：测试环境[测试环境无需绑定仅用于验证] 2：生产环境)：")
        if len(env) == 0 :
            print("请选择连接环境！！")
            continue
        elif env != "1" and env != "2":
            print("请选择连接环境！！")
            continue
        else:
            break

    for i in range(4):
        country_code_mobile = input("\r\n请输入开发者登录手机号(格式 0086-18633336666)：")
        if len(country_code_mobile) == 0:
            print("请输入手机号码！！")
            continue
        else:
            str_arr = country_code_mobile.split('-')
            if len(str_arr) < 2:
                print("手机号码格式不正确！！!")
                continue
            country_code = str_arr[0]
            mobile = str_arr[1]
            if not is_mobile(mobile, country_code):
                print("手机号码格式不正确！！!")
                continue
            break

    for i in range(4):
        key = input("\r\n请输入开发者私钥[仅用于开发者身份签名验证]：")
        if len(key) == 0:
            print("开发者私钥输入不正确！！")
            continue
        else:
            try:
                if not key.startswith('-----'):
                    key = "-----BEGIN RSA PRIVATE KEY-----\n" + key + "\n-----END RSA PRIVATE KEY-----"
                resp_code, resp_msg = network_request.send_auth_code(env, country_code, mobile, key)
                if resp_code != '0000':
                    print(f"验证码发送失败！错误码：{resp_code}，错误信息：{resp_msg}")
                else:
                    print("验证码发送成功，请注意查收！")
                    break
            except Exception as e:
                print("验证码发送失败，请重试！！")
                logging.error(traceback.print_exc())

    for i in range(4):
        code = input("\r\n请输入手机验证码：")
        if len(code) == 0:
            print("手机验证码输入不正确！！")
            continue
        else:
            try:
                device_no = network_utils.get_mac_address()
                resp_code, resp_msg = network_request.send_bind_request(env, country_code, mobile, key, code, device_no)
                if resp_code != '0000':
                    if i == 3:
                        print(f"设备绑定失败！错误码：{resp_code}，错误信息：{resp_msg}")
                    else:
                        print(f"错误次数过多请联系客服处理！错误码：{resp_code}，错误信息：{resp_msg}")
                else:
                    print(f"手机号: {mobile}, 设备号: {device_no}  绑定成功！")
                    break
            except Exception as e:
                print("设备绑定失败，请重试！！")
                logging.error(traceback.print_exc())
    exit(0)