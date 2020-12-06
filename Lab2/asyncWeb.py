import asyncio


async def dispatch(reader, writer):
    httpheader = HTTPHeader()
    cnt = 0
    while True:
        data = await reader.readline()
        message = data.decode()
        if cnt == 0:
            httpheader.parse_header(message)
            print(httpheader.get('path'))
            cnt = cnt + 1
        if data == b'\r\n':
            break
    writer.writelines([
        b'HTTP/1.0 200 OK\r\n', b'Content-Type:text/html; charset=utf-8\r\n',
        b'Connection: close\r\n', b'\r\n',
        b'<html><body>Hello World!<body></html>\r\n', b'\r\n'
    ])
    await writer.drain()
    writer.close()


keys = ('method', 'path')


class HTTPHeader:
    def __init__(self):
        self.headers = {key: None for key in keys}

    def parse_header(self, line):
        fileds = line.split(' ')
        if fileds[0] == 'GET' or fileds[0] == 'POST' or fileds[0] == 'HEAD':
            self.headers['method'] = fileds[0]
            self.headers['path'] = fileds[1]

    def get(self, key):
        return self.headers.get(key)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    coro = asyncio.start_server(dispatch, '127.0.0.1', 8080, loop=loop)
    server = loop.run_until_complete(coro)
    # Serve requests until Ctrl+C is pressed
    print('Serving on {}'.format(server.sockets[0].getsockname()))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    # Close the server
    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()
