import os
import asyncio
import argparse
import mimetypes
import chardet
from urllib import parse

PORT = 8080
base_url = '.'


def build_404():
    return [
        b'HTTP/1.0 404 Not Found\r\n',
        b'Content-Type: text/html; charset=utf-8\r\n',
        b'Accept-Ranges: bytes\r\n', b'Connection: close\r\n', b'\r\n',
        b'<h1 style="text-align: center">404 NOT FOUND</h1>', b'\r\n'
    ]


def build_405():
    return [
        b'HTTP/1.0 405 Method Not Allowed\r\n',
        b'Content-Type: text/html; charset=utf-8\r\n',
        b'Accept-Ranges: bytes\r\n', b'Connection: close\r\n', b'\r\n',
        b'<h1 style="text-align: center">405 Method Not Allowed</h1>', b'\r\n'
    ]


def build_directory(request_dir, isHead):
    system_url = base_url + request_dir
    content = '<html><head><title>Index of %s</title></head><body bgcolor="white"><h1>Index of %s</h1><hr><pre>' % (
        request_dir, request_dir)
    parent_dir = '/' if request_dir == '/' else os.path.dirname(request_dir)
    line_template = '<a href=' + request_dir + '/{}>{}</a><br>' if request_dir != '/' else '<a href={}>{}</a><br>'
    if request_dir != '/':
        content += '<a href={}>../</a><br>'.format(parent_dir)
    for item in os.listdir(system_url):  #
        if os.path.isdir(os.path.join(system_url, item)):
            content += line_template.format(parse.quote(item), item + '/')
        else:
            content += line_template.format(parse.quote(item), item)

    content += '</pre><hr></body></html>'

    response = [
        b'HTTP/1.0 200 OK\r\n', b'Content-Type: text/html; charset=utf-8\r\n',
        b'Accept-Ranges: bytes\r\n', b'Connection: close\r\n', b'\r\n'
    ]
    if not isHead:
        response.append(content.encode())
        response.append(b'\r\n')
    return response


def build_partial_directory(request_dir, start, end, isHead):
    system_url = base_url + request_dir

    content = '<html><head><title>Index of %s</title></head><body bgcolor="white"><h1>Index of %s</h1><hr><pre>' % (
        request_dir, request_dir)
    parent_dir = '/' if request_dir == '/' else os.path.dirname(request_dir)
    line_template = '<a href=' + request_dir + '/{}>{}</a><br>' if request_dir != '/' else '<a href={}>{}</a><br>'
    if request_dir != '/':
        content += '<a href={}>../</a><br>'.format(parent_dir)

    for item in os.listdir(system_url):  #
        if os.path.isdir(os.path.join(system_url, item)):
            content += line_template.format(parse.quote(item), item + '/')
        else:
            content += line_template.format(parse.quote(item), item)

    content += '</pre><hr></body></html>'

    if start and end:
        start = int(start)
        end = int(end)
    elif start:
        start = int(start)
        end = content.__len__()
    else:
        tmp = int(end)
        end = content.__len__()
        start = end - tmp + 1
    size = end - start + 1
    page_size = content.__len__()

    response = [
        b'HTTP/1.0 206 Partial Content\r\n', b'Connection: close\r\n',
        b'Accept-Ranges: bytes\r\n',
        b'Content-Length: ' + str(size).encode() + b'\r\n',
        b'Content-Range: bytes ' + str(start).encode() + b'-' +
        str(end).encode() + b'/' + str(page_size).encode() + b'\r\n',
        b'Content-Type: text/html; charset=utf-8\r\n', b'\r\n'
    ]
    if not isHead:
        response.append(content[start:end].encode())
        response.append(b'\r\n')
    return response


def build_file(system_url, isHead):
    content = b''
    with open(system_url, 'rb') as f:
        content = f.read()
    file_size = os.path.getsize(system_url)
    file_type = str(mimetypes.guess_type(system_url)[0])
    if 'text' in file_type:
        text_type = chardet.detect(content)['encoding']  # judge encoding mode
        content_type = 'Content-Type: %s; charset=%s\r\n' % (file_type,
                                                             text_type)
    elif file_type == 'None':
        content_type = 'Content-Type: application/octet-stream\r\n'
    else:
        content_type = 'Content-Type: %s\r\n' % file_type

    response = [
        b'HTTP/1.0 200 OK\r\n', b'Accept-Ranges: bytes\r\n',
        b'Connection: close\r\n',
        b'Content-Length: ' + str(file_size).encode() + b'\r\n',
        content_type.encode(), b'\r\n'
    ]
    if not isHead:
        response.append(content)
    return response


def build_partial_file(system_url, start, end, isHead):
    content = b''
    if start and end:
        start = int(start)
        end = int(end)
    elif start:
        start = int(start)
        end = os.path.getsize(system_url)
    else:
        tmp = int(end)
        end = os.path.getsize(system_url)
        start = end - tmp + 1
    size = end - start + 1
    with open(system_url, 'rb') as f:
        f.seek(start)
        content = f.read(size)
    file_size = os.path.getsize(system_url)
    file_type = str(mimetypes.guess_type(system_url)[0])
    if 'text' in file_type:
        text_type = chardet.detect(content)['encoding']  # judge encoding mode
        content_type = 'Content-Type: %s; charset=%s\r\n' % (file_type,
                                                             text_type)
    elif file_type == 'None':
        content_type = 'Content-Type: application/octet-stream\r\n'
    else:
        content_type = 'Content-Type: %s\r\n' % file_type

    response = [
        b'HTTP/1.0 206 Partial Content\r\n', b'Connection: close\r\n',
        b'Accept-Ranges: bytes\r\n',
        b'Content-Length: ' + str(size).encode() + b'\r\n',
        b'Content-Range: bytes ' + str(start).encode() + b'-' +
        str(end).encode() + b'/' + str(file_size).encode() + b'\r\n',
        content_type.encode(), b'\r\n'
    ]
    if not isHead:
        response.append(content)
        response.append(b'\r\n')
    return response


async def build_response(fields):
    header = fields['Header'].split(' ')
    request_method = header[0]
    request_url = parse.unquote(header[1])
    system_url = base_url + request_url
    
    print(system_url)
    print(request_url)
    print(base_url)
    if not os.path.exists(system_url):  #
        return build_404()
    if request_method != 'GET' and request_method != 'HEAD':
        await asyncio.sleep(2)
        return build_405()

    isHead = request_method == 'HEAD'
    if os.path.isdir(system_url):  #
        if 'Range' in fields.keys():
            offset = fields['Range'].split('=')[1].split('-')
            return build_partial_directory(request_url, offset[0], offset[1],
                                           isHead)
        return build_directory(request_url, isHead)
    if 'Range' in fields.keys():
        offset = fields['Range'].split('=')[1].split('-')
        return build_partial_file(system_url, offset[0], offset[1], isHead)  #
    return build_file(system_url, isHead)  #


async def parse_header(header):
    header_list = header.decode().split('\r\n')
    ans = {'Header': header_list[0]}
    for i in range(1, len(header_list)):
        tmp = header_list[i].split(': ')
        if len(tmp) < 2:
            break
        if len(tmp[0]) != 0:
            ans[tmp[0]] = tmp[1]
    return ans


async def dispatch(reader, writer):
    data = await reader.read(2048)
    print('Get request: {')
    print(data.decode())
    print('}')
    fields = await parse_header(data)
    response = await build_response(fields)
    print('Send response: {')
    for i in response:
        if i == b'\r\n':
            break
        print(i.decode(), end='')
    print('}')
    client = writer.get_extra_info('peername')
    print(
        'An HTTP session between "(\'127.0.0.1\', {})" and "{}" is over.\n\n'.
        format(PORT, client))
    writer.writelines(response)
    await writer.drain()
    writer.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Simple Web File Browser')
    parser.add_argument(
        '--port',
        type=int,
        default=8080,
        help='an integer for the port of the simple web file browser')
    parser.add_argument(
        '--dir',
        type=str,
        default="./",
        help='The Directory that the browser should display for home page')
    args = parser.parse_args()
    print("server run at port %d" % args.port)
    print("server run at dir %s" % args.dir)
    PORT = args.port
    base_url = os.path.abspath(args.dir)
    loop = asyncio.get_event_loop()
    coro = asyncio.start_server(dispatch, '127.0.0.1', PORT, loop=loop)
    server = loop.run_until_complete(coro)
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        exit()
    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()
