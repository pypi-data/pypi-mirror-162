import asyncio

import _asyncio


async def fun1():
    print("start fun1")
    await asyncio.sleep(1)
    print("done fun1")
    return "fun1"


async def fun2():
    print("start fun2")
    await fun1()
    print("done fun2")
    return "fun2"


task_list = [fun1(), fun2()]

done, pending = asyncio.run(asyncio.wait(task_list))

# print(done)
# print(pending)

assert isinstance(done, set)
res = done.pop()
assert isinstance(res, _asyncio.Task)
print(res.result())
print(res.get_name())
print(res.get_coro())
print(res.get_stack())
print(res)
