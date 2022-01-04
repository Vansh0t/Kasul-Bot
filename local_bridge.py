import asyncio
from asyncio.events import get_running_loop
import json
from web_cmd import process_cmd


async def handle_connection(stream_reader:asyncio.StreamReader, stream_writer:asyncio.StreamWriter):
    rec_bytes = await stream_reader.read(4096)
    js = json.loads(rec_bytes)
    resp = await process_cmd(js['cmd'], js['args'])
    stream_writer.write(resp.encode())
    await stream_writer.drain()

async def local_server(ip, port):
    try:
        server = await asyncio.start_server(handle_connection, ip, int(port), limit=4096)
        print(f'Local server for web controls started on {ip}:{port}')
        async with server:
            await server.serve_forever()
        
    except Exception as e:
        print(f'Unable to start local server. {e}')
        get_running_loop().stop()
    
    