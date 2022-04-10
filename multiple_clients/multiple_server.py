#!/usr/bin/env python3

import asyncio

async def echo_client(reader, writer):
    while True:
        request = (await reader.read(255)).decode('utf8')
        if not request: break
        writer.write(request.encode('utf8'))
        await writer.drain()
    writer.close()
    
async def main(host, port):
    server = await asyncio.start_server(echo_client, host, port)
    await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main('127.0.0.1', 8000))
        
        
        
