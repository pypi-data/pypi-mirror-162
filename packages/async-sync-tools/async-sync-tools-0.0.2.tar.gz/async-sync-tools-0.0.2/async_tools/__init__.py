import os


from .asyncio import is_async
from .sync import async_to_sync

if os.getenv('USE_ASYNCIO'):
    from .asyncio import sync_to_async

else:
    from .sync import sync_to_async
