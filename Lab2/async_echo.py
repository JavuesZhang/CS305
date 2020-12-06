import asyncio


async def dispatch(reader, writer):

    while True:
        writers = []
        data = await reader.readline()
        if not data or data == b'exit\r\n':
            print('Exit successfully.')
            break
        # print(1,reader, 2,writer)
        writers.append(writer)
        client = writer.get_extra_info('peername')
        print('{} sent: {}'.format(client, data.decode()))
        # print(client)
        message = 'your msg {} \r\n'.format(data.decode()).encode()
        for i in writers:
            i.write(message)
        await writer.drain()
    writer.close()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    coro = asyncio.start_server(dispatch, '127.0.0.1', 5555, loop=loop)
    server = loop.run_until_complete(coro)
    # print(server)
    print('Serving on {}'.format(server.sockets[0].getsockname()))

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass

    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()
