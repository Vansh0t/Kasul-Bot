from utils import get_yt_data_async

import pytest
import asyncio


@pytest.fixture
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop

@pytest.mark.asyncio
async def tests(event_loop):
    data = await get_yt_data_async('https://www.youtube.com/watch?v=vDzwyC0UbLU')
    assert type(data) is tuple and len(data)==3