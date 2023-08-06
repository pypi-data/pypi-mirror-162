from jtt_tm_utils.sync_basedata import data_manager
import aioredis
import os
import asyncio
import logging
import functools


import unittest
import json
from jtt_tm_utils.timeutil import linux_timestamp
from datetime import datetime
carid ='737-V2'

class CliTestCase(unittest.TestCase):
    def setUp(self):
        async def _setup():
            redis = await aioredis.create_redis_pool('redis://192.168.101.74:6390/0')
            self.manager.config(redis,['vehicle','vehicle.config'])
            await redis.hset('bd:vehicle:%s' % carid,'writer','candy')
            return redis

            #

        logging.basicConfig(level=10, format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
        self.loop =asyncio.get_event_loop()
        self.manager = data_manager

        self.redis =self.loop.run_until_complete(_setup())



    # def test_up_project(self):
    #     os.chdir(os.path.join(self.projectname))
    #     up_project()


    def test_makemethod(self):

        async def set_writer():
            await self.redis.hset('bd:vehicle:%s' % carid, 'writer', 'candyabc')
            await self.redis.zadd('bd_updatekeys',linux_timestamp(), 'bdupd.vehicle.%s_{"time": %s, "act": "upd", "tables": ["vehicle"]}' %(carid,linux_timestamp()))
        async def write_synctime():
            await self.redis.hset('sync_record','lastmodifytime',datetime.now().strftime('%Y%m%d%H%M%S%f'))
            await self.redis.zadd('bd_updatekeys',linux_timestamp(), 'bdupd.basedata.recreateall_{"act":"upd","time":1623900283,"tables":["recreateall"]}')
            print('write_synctime')

        asyncio.ensure_future(data_manager.sync_data())
        self.loop.run_until_complete(asyncio.sleep(10))
        vt = self.loop.run_until_complete(self.manager.get_vehicle(carid))
        assert vt['writer'] == 'candy'
        self.loop.run_until_complete(set_writer())
        # self.redis.publish('bdupd.vehicle.%s' % carid,
        #                    json.dumps({"act": "upd", "time": linux_timestamp(), "tables": ["vehicle"]}))
        self.loop.run_until_complete(write_synctime())
        self.loop.run_until_complete(asyncio.sleep(40))

        # self.manager.custom_reload()
        # self.manager.custom_reload_item('vehicle', carid)
        vt = self.loop.run_until_complete(self.manager.get_vehicle(carid))
        assert vt['writer']=='candyabc','vt write is not valid %s' % vt['writer']
        print('read write ok %s' % vt['writer'])
        self.loop.run_forever()


