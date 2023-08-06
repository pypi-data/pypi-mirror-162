import asyncio
import json
from datetime import datetime
from collections import defaultdict
from .log import logger


DEFAULT_NAMES=[('vehicle','carid,dvrid1,fleetid,vtid'),
               'accredituser']

UPDATE_ASSOCIATIONS={'vehicle':['vehicle.','device.']}

NullObj ={}

def data_isnull(data):
    return data ==NullObj

async def get_last_modifytime(rds_r):
    # 有可能新旧同步程序同时运行，需取最新变更值
    async def get_last_time(rds_key):
        try:
            last_mdy_time =await rds_r.hget(rds_key, 'lastmodifytime')
        except Exception as e:
            logger.error('redis error:%s'%str(e))
            last_mdy_time = None
        last_mdy_time = last_mdy_time.decode()\
            if last_mdy_time is not None else '20010101010101010101'
        return datetime.strptime(last_mdy_time, '%Y%m%d%H%M%S%f')
    return await get_last_time('sync_record')

async def read_data_as_dict(rds,rds_key,fields=None):
    if fields is None:
        data = await rds.hgetall(rds_key)
        if data:
            return {k.decode(): v.decode() for k, v in data.items()}
    else:
        data = await rds.hmget(rds_key, *fields)
        if data:
            obj = {k: v.decode() for (k, v) in zip(fields, data) if v is not None}
            return obj
    return NullObj

class SyncBasedataManage():
    def __init__(self):
        self._tasks =[]
        self._redis =None
        self.mappings ={}
        self.names =[]
        self.cache =defaultdict(dict)
        # self.sync_task =None

        # self.clear_all()

    def update_associations(self,key):
        re =[key]
        conditions = UPDATE_ASSOCIATIONS.get(key)
        if conditions:
            for condition in conditions:
                re+=list(filter(lambda name:name.startswith(condition),self.names))

        return re

    def config(self,redis,names=DEFAULT_NAMES,loop=None):
        def make_func(name):
            def _method(self,key):
                return self.get_bdobj(name,key)

            return _method

        self._redis =redis
        for cname in names:
            if type(cname)==tuple:
                name, fields = cname
                self.mappings[name]=fields.split(',')

            else:
                name =cname
            self.names.append(name)
            _method_name = 'get_%s' % name.replace('.', '_')
            if not hasattr(self.__class__,_method_name):
                _method = make_func(name)
                setattr(self.__class__, _method_name, _method)
        # self.names =names
        if loop is not None:
            self._tasks.append(loop.create_task(self.sync_data()))

    @property
    def rds(self):
        assert self._redis is not None, '%s :please config redis first.' % self.__class__.__name__
        return self._redis

    def clear_all(self):
        self.cache.clear()


    async def sync_data(self):
        last_modifytime =await get_last_modifytime(self.rds)
        # 避免频繁重启时，频繁访问redis
        await asyncio.sleep(10)
        while True:
            try:
                logger.debug('SyncBasedataManage.sync_data')
                last_modifytime_local =await get_last_modifytime(self.rds)
                if last_modifytime_local > last_modifytime:
                    updatedatas = await self.rds.zrangebyscore('bd_updatekeys',int(last_modifytime.timestamp()), float('inf'))
                    for ud in updatedatas:
                        ud_key = ud.decode().split('_')[0]
                        if ud_key.startswith('bdupd.'):
                            [name,key] = ud_key.split('.')[-2:]
                            if name =='basedata' and key =='recreateall':
                                logger.info('ready recreatecall')
                                handled = self.custom_reload()
                                if not handled:
                                    self.clear_all()

                            else:
                                bd_names = self.update_associations(name)
                                for bd_name in bd_names:
                                    handled =self.custom_reload_item(bd_name,key)
                                    if not handled :
                                        self.remove_bdobj(bd_name,key)

                last_modifytime = last_modifytime_local
            except Exception as e:
                logger.error('sync_basedata error:%s' % str(e))
            finally:
                await asyncio.sleep(30)
    def custom_reload(self):
        return False

    def custom_reload_item(self,name,key):
        return False

    async def get_bdobj(self,name,key,key_type='hash'):
        assert name in self.names,'not set config %s' % name
        obj =(self.cache.get(name) or {}).get(key)
        # obj = self.cache[name].get(key)
        if obj is None:
            rds_key = 'bd:%s:%s' % (name, key)
            fields =self.mappings.get(name)
            obj =None
            if key_type =='hash':
                obj = await read_data_as_dict(self.rds,rds_key,fields)
            elif key_type =='string':
                data = await self.rds.get(rds_key)
                if data is not None:
                    try:
                        obj = json.loads(data.decode())
                    except Exception as e:
                        logger.error('key:%s load error:%s' %(rds_key,str(e)))
            else:
                logger.error('key:%s not support key_type:%s' %(rds_key,key_type))
            if data_isnull(obj):
                logger.warning('the %s(%s) is not exist!' % (name, key))
                obj =None
            # if self.cache.get(name) is None:
            #     self.cache[name] = {}
            self.add_bdobj(name,key,obj)
            return obj
        return obj


    def add_bdobj(self,name,key,obj):
        self.cache[name][key] = obj

    def remove_bdobj(self,name,key):
        if self.cache.get(name):
            try:
                self.cache[name].pop(key)
            except:
                pass


    async def event_config(self,carid,evcode):
        config = await self.get_vehicle_config(carid)
        if config is not None:
            data = config.get('event_params_%s' % evcode)
            if data:
                return json.loads(data)
        return NullObj

    async def get_e_stop(self,imsi):
        return await self.get_bdobj('estop',imsi,'string')

    async def get_vehicletype(self,id):
        return await self.get_bdobj('vehicletype',id,'string')

class MapSyncManager(SyncBasedataManage):
    def __init__(self,has_map_dvrid=False):
        super().__init__()
        self.has_map_dvrid =has_map_dvrid
        self.dvrid_carid_map ={}
        # self.has_dvrid = has_map_dvrid


    def add_bdobj(self,name,key,obj):
        super().add_bdobj(name,key,obj)
        if self.has_map_dvrid and name =='vehicle' and obj is not None and obj.get('dvrid1') is not None:
            self.dvrid_carid_map[obj['dvrid1']]=key

    def remove_bdobj(self,name,key):
        if self.has_map_dvrid and name == 'vehicle':
            obj = self.cache[name].get(key)
            if obj is not None and obj.get('dvrid1') is not None:
                try:
                    self.dvrid_carid_map.pop(obj['dvrid1'])
                except:
                    pass

        super().remove_bdobj(name, key)

    def clear_all(self):
        super().clear_all()
        self.dvrid_carid_map.clear()

    def custom_reload(self):

        vt_keys = self.cache['vehicle'].keys()

        self.clear_all()

        for key in vt_keys:
            asyncio.ensure_future(self.get_bdobj('vehicle',key))

        return True

    def custom_reload_item(self,name,key):
        self.remove_bdobj(name,key)
        if name =='vehicle' and self.has_map_dvrid:
            asyncio.ensure_future(self.get_bdobj(name,key))
        return True


# managers={'default':SyncBasedataManage(),
#           'map_dvrid1':MapSyncManager(True)}
# def get_manager():
#     import os
#     mode = os.getenv('SYNC_MANAGER','default')
#     if mode =='default':
#         return SyncBasedataManage()
#     elif mode =='map_dvrid1':
#         return MapSyncManager(True)

data_manager=MapSyncManager()


