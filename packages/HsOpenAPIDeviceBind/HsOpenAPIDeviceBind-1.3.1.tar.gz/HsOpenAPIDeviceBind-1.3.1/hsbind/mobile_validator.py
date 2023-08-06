#!/usr/bin/env python
# -*- coding:utf-8 -*-

import re

from hsbind.common_utils import get_logger

logging = get_logger(__name__)

country_code_chn = "0086"
country_code_hkg = "0852"
country_code_mac = "0853"
country_code_twn = "0886"
country_code_sgp = "0065"

country_code_chn_str = "CHN"
country_code_hkg_str = "HKG"
country_code_mac_str = "MAC"
country_code_twn_str = "TWN"
country_code_sgp_str = "SGP"

pattern_simple = "^\\d{5,15}$"
pattern_chn = "^1(3\\d|4\\d|5\\d|6[23567]|7\\d|8\\d|9\\d)\\d{8}$"
pattern_hkg = "^[3-9]\\d{7}$"
pattern_mac = "^6(2|3|5|6|8)\\d{6}$"
pattern_twn = "^0?9\\d{8}$"
pattern_sgp = "^[89]\\d{7}$"


def is_mobile(mobile, country_code):
    if len(mobile) == 0 or len(country_code) == 0:
        return False

    if is_cn_code(country_code):
        return validate(mobile)

    if is_hk_code(country_code):
        return validate_hk(mobile)

    if is_mac_code(country_code):
        return validate_mac(mobile)

    if is_twn_code(country_code):
        return validate_twn(mobile)

    if is_sgp_code(country_code):
        return validate_sgp(mobile)

    return re.match(pattern_simple, mobile)


def is_cn_code(code):
    return code == country_code_chn or code == country_code_chn_str


def is_hk_code(code):
    return code == country_code_hkg or code == country_code_hkg_str


def is_mac_code(code):
    return code == country_code_mac or country_code_mac_str


def is_twn_code(code):
    return code == country_code_twn or code == country_code_twn_str


def is_sgp_code(code):
    return code == country_code_sgp or code == country_code_sgp_str


def validate(mobile):
    if len(mobile) == 0:
        return False
    res = re.match(pattern_chn, mobile)
    if res:
        return True
    else:
        return False


def validate_hk(mobile):
    if len(mobile) == 0:
        return False
    res = re.match(pattern_hkg, mobile)
    if res:
        return True
    else:
        return False


def validate_mac(mobile):
    if len(mobile) == 0:
        return False
    res = re.match(pattern_mac, mobile)
    if res:
        return True
    else:
        return False


def validate_twn(mobile):
    if len(mobile) == 0:
        return False
    res = re.match(pattern_twn, mobile)
    if res:
        return True
    else:
        return False


def validate_sgp(mobile):
    if len(mobile) == 0:
        return False
    res = re.match(pattern_sgp, mobile)
    if res:
        return True
    else:
        return False
