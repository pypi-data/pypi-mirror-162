import base64
import hashlib
import random
from string import ascii_letters


def gfw_decode(content: str):
    b64_str = content[16:]
    index = b64_str.find('=')
    if index == -1:
        return b64decode(b64_str[::-1])
    else:
        return b64decode(b64_str[:index][::-1] + b64_str[index:])


def gfw_encode(content: str):
    b64_str = b64encode(content)
    index = b64_str.find('=')
    random_str = ''.join(random.choices(ascii_letters, k=16))
    if index == -1:
        return random_str + b64_str[::-1]
    else:
        return random_str + b64_str[:index][::-1] + b64_str[index:]


def b64encode(content):
    return base64.b64encode(content.encode('utf-8')).decode('utf-8')


def b64decode(content):
    return base64.b64decode(content.encode('utf-8')).decode('utf-8')


def b32encode(content):
    return base64.b32encode(content.encode('utf-8')).decode('utf-8')


def b32decode(content):
    return base64.b32decode(content.encode('utf-8')).decode('utf-8')


def md5(content):
    return hashlib.md5(content.encode()).hexdigest()


