import asyncio
import functools


def run_async(async_function):

    @functools.wraps(async_function)
    def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(async_function(*args, **kwargs))
    return wrapper