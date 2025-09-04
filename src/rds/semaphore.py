import math
import time
import uuid

from src.rds import REDIS, PREFIX

_PREFIX = f'{PREFIX}:semaphore'


def _key(v: str) -> str:
    return f'{_PREFIX}:{v}'


class Semaphore:
    def __init__(
            self,
            id_: str = None,
            limit: int = 1,
            timeout: float = None,
            raise_err: bool = False,
    ):
        if id_ is None:
            id_ = str(uuid.uuid4())
        id_ = id_.replace(':', '-')
        self._id: str = id_

        self._limit = int(limit)

        if timeout is None:
            timeout = math.inf
        self._timeout = float(timeout)

        self._raise_err = raise_err

    @property
    def id(self) -> str:
        return self._id

    @property
    def limit(self) -> int:
        return self._limit

    @property
    def timeout(self) -> float:
        return self._timeout

    def __enter__(self) -> bool:
        return self.acquire()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()

    def acquire(self, timeout: float = None) -> bool:
        start_time = time.time()
        if timeout is None:
            timeout = self._timeout
        timeout = float(timeout)

        script = """
        local key = KEYS[1]
        local setnx_result = redis.call('SETNX', key, 0)
        if setnx_result == 1 then
            redis.call('INCR', key)
            return 1
        else
            local current = tonumber(redis.call('GET', key))
            if current < #LIMIT then
                redis.call('INCR', key)
                return 1
            else
                return 0
            end
        end
        """.replace('#LIMIT', str(self._limit))
        script_sha = REDIS.script_load(script)

        key = _key(self._id)
        while True:
            result = REDIS.evalsha(script_sha, 1, key)
            if result == 0:
                if time.time() - start_time > timeout:
                    if self._raise_err:
                        raise TimeoutError(f'获取信号量({self._id})超时 ({timeout}s)')
                    return False
                time.sleep(.1)
                continue
            elif result == 1:
                return True
            else:
                raise ValueError(f'错误的redis返回值: {result}')

    def release(self):
        script = """
        local key = KEYS[1]
        local exists = redis.call('EXISTS', key)
        if exists == 0 then
            return 0
        else
            local current = tonumber(redis.call('GET', key))
            if current > 0 then
                redis.call('DECR', key)
                return 1
            else
                return 0
            end
        end
        """
        script_sha = REDIS.script_load(script)
        result = REDIS.evalsha(script_sha, 1, _key(self._id))
        return bool(result)

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


Semaphore.clear()
