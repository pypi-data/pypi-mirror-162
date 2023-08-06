#!/usr/bin/env python
# -*- coding: utf-8 -*-
import base64

from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5 as Sign_Cipher_pkcs1_v1_5


def rsa_sign(encrypted_message: bytes, rsa_private_key: str) -> bytes:
    """RSA私钥签名"""
    if type(encrypted_message) is not bytes:
        encrypted_message = bytes(encrypted_message, encoding='utf-8')
    private_key_object = RSA.importKey(rsa_private_key)
    signer = Sign_Cipher_pkcs1_v1_5.new(private_key_object)
    digest = SHA.new()
    digest.update(encrypted_message)
    return signer.sign(digest)
    # return base64.b64encode(signature).decode("utf-8")

def bytes_to_str(bytes_obj: bytes) -> str:
    """bytes转str"""
    if type(bytes_obj) is not str:
        str_obj = bytes_obj.decode("utf-8")
    else:
        str_obj = bytes_obj
    return str_obj
