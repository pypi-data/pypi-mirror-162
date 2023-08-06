# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File:           aes_encrypt.py
   Description:    AES加密解密实现
   Author:        
   Create Date:    2020/07/30
-------------------------------------------------
   Modify:
                   2020/07/30:
-------------------------------------------------
"""
from Crypto.Cipher import AES
import base64


def aes_encrypt(key, data):
    """
    AES的ECB模式加密方法
    :param key: 密钥
    :param data: 被加密字符串（明文）
    :return: 密文
    """

    # Bytes
    BLOCK_SIZE = 16

    # 字符串补位
    pad = lambda s:\
        s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * chr(BLOCK_SIZE - len(s) % BLOCK_SIZE)

    key = key.encode('utf8')
    data = pad(data)
    cipher = AES.new(key, AES.MODE_ECB)
    # 加密后得到的是bytes类型的数据，使用Base64进行编码,返回byte字符串
    result = cipher.encrypt(data.encode())
    encode_str = base64.b64encode(result)
    enc_text = encode_str.decode('utf8')
    return enc_text


def aes_decrypt(key, data):
    """
    AES解密
    :param key: 密钥
    :param data: 加密后的数据（密文
    :return: 明文
    """

    # 去补位
    unpad = lambda s: s[:-ord(s[len(s) - 1:])]

    key = key.encode('utf8')
    data = base64.b64decode(data)
    cipher = AES.new(key, AES.MODE_ECB)

    text_decrypted = unpad(cipher.decrypt(data))
    text_decrypted = text_decrypted.decode('utf8')
    return text_decrypted


if __name__ == '__main__':
  pass

