import redis
r = redis.Redis(host='redis-10145.c258.us-east-1-4.ec2.cloud.redislabs.com', port=10145, db=0, password="pm4Bk6JwEIQtmDeuJPaQdz01TfRcjYCo")
print(r)
ret = r.set('foo', 'bar')
print(ret)
ret = r.get('foo').decode('utf-8')
print(ret)
