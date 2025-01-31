# -*- coding: utf-8 -*-
# @File : FileBrowser.py
import argparse
import asyncio
import os
import mimetypes
from urllib import parse
import chardet

err405 = [
    b'HTTP/1.0 405 Method Not Allowed\r\n', b'Connection: close\r\n',
    b'Content-Type:text/html; charset=utf-8\r\n', b'\r\n',
    b'<html><body>405 Method Not Allowed<body></html>\r\n', b'\r\n'
]

err404 = [
    b'HTTP/1.0 404 Not Found\r\n', b'Connection: close\r\n',
    b'Content-Type:text/html; charset=utf-8\r\n', b'\r\n',
    b'<html><body>404 Not Found<body></html>\r\n', b'\r\n'
]


def get_dir_html(dir_path):  # 请求为文件夹时
    body = '<html><head><title>Index of %s</title></head><body bgcolor="white"><h1>Index of %s</h1><hr><pre>' % (
        dir_path, dir_path)
    for file in os.listdir(dir_path):
        body += '<a href="%s">%s</a><br>' % (dir_path + '/' + file, file)
    body += '</pre><hr></body></html>'
    content_length = 'Content-Length: %s; charset=utf-8\r\n' % str(
        len(body.encode()))
    html = [
        b'HTTP/1.0 200 OK\r\n', b'Connection: close\r\n',
        b'Content-Type:text/html; charset=utf-8\r\n',
        content_length.encode(), b'\r\n',
        body.encode(), b'\r\n'
    ]
    return html


def get_file_html(file_path, is_head):  # 请求为文件时
    file_type = str(mimetypes.guess_type(file_path)[0])  # 获取文件content-type
    file = open(file_path, 'rb')
    data = file.read()
    if 'text' in file_type:
        text_type = chardet.detect(data)['encoding']  # 判断文本文档的编码
        content_type = 'Content-Type: %s; charset=%s\r\n' % (file_type,
                                                             text_type)
    else:
        content_type = 'Content-Type: %s\r\n' % file_type

    content_length = 'Content-Length: %s\r\n' % str(os.path.getsize(file_path))
    if is_head:
        html = [
            b'HTTP/1.0 200 OK\r\n', b'Connection: close\r\n',
            content_type.encode(),
            content_length.encode(), b'\r\n'
        ]
    else:
        html = [
            b'HTTP/1.0 200 OK\r\n', b'Connection: close\r\n',
            content_type.encode(),
            content_length.encode(), b'\r\n', data, b'\r\n'
        ]
    file.close()
    return html


def do_get(path):
    if os.path.isdir(path):
        res = get_dir_html(path)
    elif os.path.isfile(path):
        res = get_file_html(path)
    else:
        res = err404

    return res


async def dispatch(reader, writer):
    data = await reader.read(2048)
    data = data.decode().split('\r\n')
    print(data)
    head = data[0].split(' ')
    res = err405  # 默认返回405
    if len(head) > 0:
        if head[0] == 'GET':
            file_path = '.' + head[1]
            file_path = parse.unquote(file_path)  # 解析中文字符
            res = do_get(file_path)
        else:
            if head[0] == 'HEAD':
                file_path = '.' + head[1]
                file_path = parse.unquote(file_path)  # 解析中文字符
                res = do_get(file_path)
    writer.writelines(res)
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

    loop = asyncio.get_event_loop()
    coro = asyncio.start_server(dispatch, '127.0.0.1', args.port, loop=loop)
    server = loop.run_until_complete(coro)
    # print('Serving on{}'.format(server.sockets[0].getsockname()))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        exit()
    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()
