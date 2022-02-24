import asyncio


class AsyncQueue(asyncio.Queue):
    """
    asyncio.Queue with a peek method added.
    """

    async def peek(self):
        while self.empty():
            getter = self._loop.create_future()
            self._getters.append(getter)
            try:
                await getter
            except:  # noqa: E722
                getter.cancel()  # Just in case getter is not done yet.
                try:
                    # Clean self._getters from canceled getters.
                    self._getters.remove(getter)
                except ValueError:
                    # The getter could be removed from self._getters by a
                    # previous put_nowait call.
                    pass
                if not self.empty() and not getter.cancelled():
                    # We were woken up by put_nowait(), but can't take
                    # the call.  Wake up the next in line.
                    self._wakeup_next(self._getters)
                raise
        return self.peek_nowait()

    def peek_nowait(self):
        if self.empty():
            raise asyncio.QueueEmpty
        item = self._peek()
        self._wakeup_next(self._putters)
        return item

    def _peek(self):
        return self._queue[0]