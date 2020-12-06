import dnslib
import time
import random
import socket

cache = {}
ROOTSERVERS = [('a.root-servers.net', '198.41.0.4'),
               ('b.root-servers.net', '199.9.14.201'),
               ('c.root-servers.net', '192.33.4.12'),
               ('d.root-servers.net', '199.7.91.13'),
               ('e.root-servers.net', '192.203.230.10'),
               ('f.root-servers.net', '192.5.5.241'),
               ('g.root-servers.net', '192.112.36.4'),
               ('h.root-servers.net', '198.97.190.53'),
               ('i.root-servers.net', '192.36.148.17'),
               ('j.root-servers.net', '192.58.128.30'),
               ('k.root-servers.net', '193.0.14.129'),
               ('l.root-servers.net', '199.7.83.42'),
               ('m.root-servers.net', '202.12.27.33')]


class Record():
    def __init__(self, currentTime, ttl, header, rr, auth, ar):
        self.currentTime = currentTime
        self.ttl = ttl
        self.header = header
        self.rr = rr
        self.auth = auth
        self.ar = ar


# check whether in cache
def CheckInCache(qname, qtype):
    if qname not in cache:
        cache[qname] = {}
        return False
    if qtype not in cache[qname]:
        return False
    # out of date
    nowTime = time.time()
    if nowTime - cache[qname][qtype].currentTime >= cache[qname][qtype].ttl:
        del cache[qname][qtype]
        return False
    return True


# get record from cache and update ttl
def GetFromCache(qname, qtype, header):
    record: Record = cache[qname][qtype]
    nowTime = int(time.time())
    deltaTime = nowTime - record.currentTime
    for rr in record.rr:
        rr.ttl -= deltaTime
    record.currentTime = nowTime
    record.ttl -= deltaTime
    cacheRecord = dnslib.DNSRecord(dnslib.DNSHeader(id=header.id,
                                                    qr=header.qr,
                                                    aa=0,
                                                    ra=0),
                                   q=dnslib.DNSQuestion(qname, qtype),
                                   rr=record.rr)
    cacheRecord.header.qr = 1
    return bytes(cacheRecord.pack())


# write record into cache
def WriteToCache(qname, qtype, message):
    dnsMsg = dnslib.DNSRecord.parse(message)
    ttl = float("inf")
    for rr in dnsMsg.rr:
        ttl = min(ttl, rr.ttl)
    record: Record = Record(int(time.time()), ttl, dnsMsg.header, dnsMsg.rr,
                            dnsMsg.a, dnsMsg.ar)
    cache[qname][qtype] = record


if __name__ == '__main__':
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.bind(('127.0.0.1', 12000))
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    print('The server is ready to receive...')
    while True:
        message, client_addr = server.recvfrom(2048)
        req = dnslib.DNSRecord.parse(message)
        qname, qtype, header = req.q.qname, req.q.qtype, req.header
        print('Query: \"%s\"' % (qname))

        if (CheckInCache(qname, qtype)):
            print('Response from cache')
            dnsMsg = GetFromCache(qname, qtype, header)
        else:
            # rd=1 then forward the query directly
            if header.rd == 1:
                print("Response from Recursive query")
                req.header.rd = 0
                message = bytes(req.pack())
                client.sendto(message, ('114.114.114.114', 53))
                dnsMsg = client.recv(2048)
                WriteToCache(qname, qtype, dnsMsg)
            else:
                print("Response from Iterative query")
                nextServer = ROOTSERVERS[random.randint(0, 12)]
                recordList = []

                while True:
                    print("Query Address: %s(%s)" %
                          (nextServer[1], nextServer[0]))
                    client.sendto(message, (nextServer[0], 53))
                    receiveMessage = client.recv(2048)
                    tempRequest = dnslib.DNSRecord.parse(receiveMessage)
                    recordList.extend(tempRequest.rr)

                    if tempRequest.header.a != 0:
                        tempRequest.rr = recordList
                        tempRequest.header.a += 1
                        receiveMessage = bytes(tempRequest.pack())
                        WriteToCache(tempRequest.q.qname, tempRequest.q.qtype,
                                     receiveMessage)
                        dnsMsg = GetFromCache(tempRequest.q.qname,
                                              tempRequest.q.qtype,
                                              tempRequest.header)
                        break
                    index = random.randint(0, tempRequest.ar.__len__() - 1)
                    nextServer = [
                        str(tempRequest.ar[index].rname),
                        str(tempRequest.ar[index].rdata)
                    ]
        server.sendto(dnsMsg, client_addr)
