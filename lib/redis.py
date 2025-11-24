import redis

# redis connection pool
pool = redis.ConnectionPool(host="localhost", port=6379, db=0)

# initilaize connection
redisConnection = redis.Redis(connection_pool=pool)
