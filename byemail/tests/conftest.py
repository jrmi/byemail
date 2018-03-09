import asyncio

import pytest

@pytest.fixture
def loop():
    asyncio.set_event_loop(None)
    return asyncio.new_event_loop()