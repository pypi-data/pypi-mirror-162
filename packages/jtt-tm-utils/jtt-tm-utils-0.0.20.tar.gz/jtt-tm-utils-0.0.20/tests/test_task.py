
import asyncio
from jtt_tm_utils.redis_manager import redis_manager
from jtt_tm_utils.jtt_task import JttTaskManager,TaskState
import aioredis

carid = '101-FX'
# class TestTask():
#     carid = '101-FX'
async def get_manager():
    await redis_manager.aload_configs(['jtt_task'])
    return JttTaskManager(redis_manager.jtt_task)

async def test_create_task():
    manager = await get_manager()
    await manager.create_task('101-FX','upgrade',{},user='super')
    # await manager.create_task('101-FX', 'upgrade', {}, user='super')
#
async def test_load_task():
    manager = await get_manager()
    await manager.create_task('101-FX', 'upgrade', {}, user='super',task_no='upgrade')
    task =await manager.load_task('101-FX','upgrade')
    assert task!=None
    assert task.taskno =='upgrade'
#
#
async def test_close_task():
    manager = await get_manager()
    await manager.create_task('101-FX', 'upgrade', {}, user='super', task_no='upgrade_close')
    await manager.close_task('101-FX', 'upgrade_close',extra='upgrade_close')
    assert await manager.load_task('101-FX', 'upgrade_close') is None


async def test_waiting_task():
    manager = await get_manager()
    task = await manager.create_task('101-FX', 'upgrade', {}, user='super',task_no='upgrade_wait')
    is_same = await manager.same_task('101-FX', 'upgrade_wait')
    assert is_same ==True
    await manager.waitting_task('101-FX',task.taskno,100,add_waiting_list=True)
    assert task.state ==TaskState.waiting
    task_no = await manager.taskno_by_ackseq('101-FX', 100)
    assert task_no == 'upgrade_wait'

async def test_pop_taskno():
    manager = await get_manager()
    taskno = await manager.pop_taskno('101-FX')
    print(taskno)

async def test_task_terminates():
    manager = await get_manager()
    carids= await manager.task_terminates()
    print(carids)