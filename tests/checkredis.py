import redis

if __name__ == '__main__':
    redis_client = redis.Redis(host='localhost', port=6379, db=0)

    print(redis_client.llen("chain"))
    print(redis_client.lrange("chain",0,-1))
    print(redis_client.flushall())