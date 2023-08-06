import os
from typing import Dict

import codefast as cf


class Authentication(object):
    @classmethod
    def exec(cls):
        d = os.path.join(os.path.expanduser("~"), '.config/textauth')
        if not cf.io.exists(d):
            cf.error('textauth not exists')
            return ""
        master = 'bDVlQnR2ZTdtM1MzcjZnVAo'
        cmd = f'openssl bf -iter 1024 -d -k {master} < {d}'
        return cf.shell(cmd)


def authc() -> Dict[str, str]:
    try:
        texts = Authentication.exec()
        dt = {}
        for ln in texts.split('\n'):
            if ln:
                k, v = ln.split(':', 1)
                dt[k] = v
        return dt
    except Exception as e:
        cf.error(e)
        return {}


def sli() -> str:
    dt = authc()
    for k, v in dt.items():
        print(f'{k:<30} : {v}')


def gunload(key: str) -> str:
    return authc().get(key, '')
