import time
from threading import Thread
from typing import Optional

import uvicorn

__all__ = ("UvicornServer",)

# see https://github.com/encode/uvicorn/discussions/1103


class UvicornServer(uvicorn.Server):
    """Threadable uvicorn server."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._thread: Optional[Thread] = None

    def run_in_thread(self):
        """Run the server in a thread."""
        thread = Thread(target=self.run)
        self._thread = thread
        thread.start()

        while not self.started:
            time.sleep(1e-3)

    def close_thread(self):
        """Close the running thread."""
        self.should_exit = True
        t = self._thread

        if t:
            t.join()

        self._thread = None
