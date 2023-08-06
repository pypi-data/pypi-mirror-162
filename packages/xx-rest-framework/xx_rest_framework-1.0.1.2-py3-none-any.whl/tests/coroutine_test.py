import asyncio
import time


async def test_coroutine_1():
    time.sleep(1)
    return "test_coroutine_1"


async def test_coroutine_2():
    await asyncio.sleep(1)
    return "test_coroutine_2"


if __name__ == '__main__':

    print("start...")
    start = time.time()
    test1 = test_coroutine_1()
    try:
        test1.send(None)
    except StopIteration as ex:
        pass
        # print(ex)
    print(f"done test1 used {time.time() - start}")

    print()

    start = time.time()
    test2 = test_coroutine_2()
    res = asyncio.run(test2)
    # print(res)

    print(f"done test2, used {time.time() - start}")
