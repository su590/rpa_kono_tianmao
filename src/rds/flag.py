import uuid

from src.rds import REDIS, PREFIX

_PREFIX = f'{PREFIX}:flag'


class Flag:
    def __init__(self, id_: str = None, ):
        if id_ is None:
            id_ = str(uuid.uuid4())
        id_ = id_.replace(':', '-')
        self._id: str = id_

    @property
    def id(self) -> str:
        return self._id

    def save(self, timeout: int = None) -> bool:
        if timeout is None:
            result = REDIS.set(f'{_PREFIX}:{self._id}', self._id, nx=True)
        else:
            result = REDIS.set(f'{_PREFIX}:{self._id}', self._id, ex=timeout, nx=True)
        return result is True

    def exist(self) -> bool:
        return REDIS.get(f'{_PREFIX}:{self._id}') is not None

    def delete(self):
        REDIS.delete(f'{_PREFIX}:{self._id}')

    @classmethod
    def clear(cls):
        key = f'{_PREFIX}:*'
        keys = []
        cursor = 0
        while True:
            cursor, partial_keys = REDIS.scan(cursor, match=key)
            keys.extend(partial_keys)
            if cursor == 0:
                break
        for k in keys:
            REDIS.delete(k)


Flag.clear()
