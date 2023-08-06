"""Service decorators and shortcuts."""

import functools


def mark_on_call(func):
    """Mark method after execution."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        """Wrapper."""
        wrapper.called = True
        return func(*args, **kwargs)

    wrapper.called = False
    return wrapper


def mark_on_call_async(func):
    """Mark async method after execution."""

    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        """Wrapper."""
        wrapper.called = True
        return await func(*args, **kwargs)

    wrapper.called = False
    return wrapper
