# -*- coding: utf-8 -*-  
"""
密码学相关工具
"""
import hashlib


class _CryptoTools:
    @classmethod
    def md5(cls, text: str | bytes, encode: str = 'utf-8') -> str:
        """
        md5加密
        :param text: 加密文本
        :param encode: 指定编码格式
        :return:
        """
        if isinstance(text, str):
            text = text.encode(encode)
        return hashlib.md5(text).hexdigest()


cryptotools = CryptoTools = _CryptoTools()
