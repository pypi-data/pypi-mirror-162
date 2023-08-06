#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from asyncio import wait, sleep, ensure_future

class Sequence:
    def __init__(self, task, repeat = 1, delay = 0, callback = lambda *args: None):
        self.task = task
        self.repeat = repeat
        self.delay = delay
        self.callback = callback
        self.results = []
    def __await__(self):
        async def __await__():
            async def futures():
                for i in range(self.repeat):
                    result = await self.task()
                    self.results.append(result)
                    await sleep(self.delay)
                    self.callback(result)
                return self.results
            return await ensure_future(futures())
        return __await__().__await__()

class Coroutine:
    def __init__(self, sequences):
        self.sequences = sequences

    def __await__(self):
        async def __await__():
            finished, _ = await wait(self.sequences)
            return [i.result() for i in finished]
        return __await__().__await__()
