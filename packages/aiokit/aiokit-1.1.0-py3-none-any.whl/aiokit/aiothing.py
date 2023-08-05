import asyncio
import logging
import signal
from typing import List
from functools import partial


class AioThing:
    def __init__(self):
        self.starts: List[AioThing] = []
        self.started = False
        self.start = self._guard_start(self.start)
        self.stop = self._guard_stop(self.stop)
        self._started_event = asyncio.Event()
        self._stopped_event = asyncio.Event()

    def _guard_start(self, fn):
        async def guarded_fn(*args, **kwargs):
            if self.started:
                return
            self.started = True
            self.setup_hooks()
            for aw in self.starts:
                logging.getLogger('debug').info({
                    'action': 'start',
                    'mode': 'aiothing',
                    'class': str(aw),
                })
                await aw.start()
            r = await fn(*args, **kwargs)
            self._started_event.set()
            return r
        return guarded_fn

    def _guard_stop(self, fn):
        async def guarded_fn(*args, **kwargs):
            if not self.started:
                return
            self.started = False
            r = await fn(*args, **kwargs)
            for aw in reversed(self.starts):
                logging.getLogger('debug').info({
                    'action': 'stop',
                    'mode': 'aiothing',
                    'class': str(aw),
                })
                await aw.stop()
            self._stopped_event.set()
            return r
        return guarded_fn

    async def start(self):
        pass

    async def stop(self):
        pass

    async def wait_started(self):
        await self._started_event.wait()

    async def wait_stopped(self):
        await self._stopped_event.wait()

    async def start_and_wait(self):
        await self.start()
        await self.wait_stopped()

    def setup_hooks(self):
        pass


class AioRootThing(AioThing):
    def setup_hooks(self):
        asyncio.get_running_loop().set_exception_handler(
            lambda loop, context: logging.getLogger('error').info({
                'action': 'error',
                'mode': 'aiothing',
                'message': str(context['message']),
                'error': str(context['exception']),
            })
        )
        for sig in (signal.SIGTERM, signal.SIGINT):
            asyncio.get_running_loop().add_signal_handler(
                sig,
                partial(asyncio.ensure_future, self._on_shutdown(signal.SIGTERM))
            )

    async def _on_shutdown(self, sig):
        logging.getLogger('debug').info({
            'action': 'received_signal',
            'mode': 'aiothing',
            'signal': str(sig),
        })
        await self.stop()
