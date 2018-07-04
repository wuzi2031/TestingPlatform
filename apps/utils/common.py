import socket


def gethost():
    # 获取本机电脑名
    myname = socket.getfqdn(socket.gethostname())
    # 获取本机ip
    myaddr = socket.gethostbyname(myname)
    host = {}
    host["name"] = myname
    host["ip"] = myaddr
    return host
