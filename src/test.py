import datetime
from datetime import timezone

# if __name__ == '__main__':
#     # dt = datetime.datetime(2024, 11, 18, 0, 0, 0)
#     # print(dt.timestamp())
#     print(datetime.datetime.fromtimestamp(1755825635, timezone(datetime.timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S'))
#     pass

import redis

def test_redis_connection():
    host = "10.1.130.103"
    port = 30937

    try:
        r = redis.Redis(host=host, port=port, decode_responses=True)
        response = r.ping()
        if response:
            print(f"✅ 成功连接到 Redis {host}:{port}")
        else:
            print(f"⚠️ 无法 ping 通 Redis {host}:{port}")
    except Exception as e:
        print(f"❌ 连接 Redis 失败: {e}")

if __name__ == "__main__":
    test_redis_connection()
