import redis

from src import get_config


def _client():
    conf = get_config('redis')
    r = redis.Redis(
        host=conf['host'],
        port=conf['port'],
        password=conf['password'],
        db=conf['db']
    )
    return r

REDIS = _client()
PREFIX = 'ktm'

# 🚀 测试连接
def test_redis_connection():
    try:
        if REDIS.ping():
            print("✅ Redis 连接成功")
        else:
            print("❌ Redis 未响应 ping")
    except redis.exceptions.ConnectionError as e:
        print(f"❌ Redis 连接失败: {e}")

if __name__ == "__main__":
    test_redis_connection()