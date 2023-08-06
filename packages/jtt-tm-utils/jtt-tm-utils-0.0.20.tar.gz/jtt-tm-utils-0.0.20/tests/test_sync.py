import pytest
from jtt_tm_utils.sync_basedata import data_manager
import aioredis
async def test_connect():
    redis =await aioredis.create_redis_pool('redis://192.168.101.70:6380/0')
    print(redis)
    data_manager.config(redis)
    data =await data_manager.get_vehicle('110-FX')
    print(data)