import asyncio
import logging
from abc import ABC, abstractmethod


class Scheduler(ABC):

    def __init__(self, timeout_seconds: float, logger: logging.Logger):
        self.timeout_seconds = timeout_seconds
        self.shutdown_event = asyncio.Event()
        self.logger = logger

    @abstractmethod
    async def execute(self):
        pass

    async def start(self):
        self.logger.info("Starting scheduler")

        while not self.shutdown_event.is_set():
            try:
                await self.execute()
            except Exception:
                self.logger.exception("Exception while executing scheduler")
            await asyncio.sleep(self.timeout_seconds)

    async def stop(self):
        self.logger.info("Stopping scheduler")
        self.shutdown_event.set()
