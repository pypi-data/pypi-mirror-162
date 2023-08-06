from aiocache import cached


class conditionally_cached(cached):
    """
    An async cache which conditionally caches values based on a function.
    This implementation is built on top of
    [cached](https://aiocache.readthedocs.io/en/latest/caches.html#cache).
    By default None values are not cached.
    """

    def __init__(self, condition=lambda r: r is not None, **kwargs):
        super().__init__(**kwargs)
        self.condition = condition

    async def decorator(self, f, *args, **kwargs):
        key = self.get_cache_key(f, args, kwargs)

        value = await self.get_from_cache(key)
        if value is not None:
            return value

        result = await f(*args, **kwargs)
        if self.condition(result):
            await self.set_in_cache(key, result)

        return result
