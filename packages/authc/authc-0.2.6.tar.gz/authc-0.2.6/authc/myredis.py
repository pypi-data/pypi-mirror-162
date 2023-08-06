from redis import StrictRedis

from authc.core import authc


def get_redis_cn():
    a = authc()
    host, port, password = a.get('ali_redis_host'), a.get(
        'ali_redis_port'), a.get('ali_redis_pass')
    return StrictRedis(host=host, port=port, password=password)


def get_redis_lab():
    # use tcp forward service to speed up redis connection
    a = authc()
    host, port, password = a.get('redis_host'), 35132, a.get('main_redis_pass')
    return StrictRedis(host=host, port=port, password=password)


def get_redis():
    a = authc()
    host, port, password = a.get('redis_host'), a.get('redis_port'), a.get(
        'redis_pass')
    return StrictRedis(host=host, port=port, password=password)


rc = type('redis_client', (object, ), {
    'cn': get_redis_cn(),
    'us': get_redis(),
    'lab': get_redis_lab()
})
