import os
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


def get_aapt():
    if "ANDROID_HOME" in os.environ:
        rootDir = os.path.join(os.environ["ANDROID_HOME"], "build-tools")
        for path, subdir, files in os.walk(rootDir):
            if "aapt" in files:
                return os.path.join(path, "aapt")
    else:
        return "ANDROID_HOME not exist"


def getApkInfo(path):
    aapt = get_aapt()
    lines = os.popen(aapt + " dump badging " + path).readlines()
    package_name = None
    launchable_activity = None
    file_name = path.split('/')[-1:][0]
    for line in lines:
        if "package:" in line:
            ws = line.split(' ')
            for w in ws:
                if 'name=' in w:
                    package_name = w.split('=')[1].replace("'", "")
        if "launchable-activity:" in line:
            ws = line.split(' ')
            for w in ws:
                if 'name=' in w:
                    launchable_activity = w.split('=')[1].replace("'", "")
    return (file_name, package_name, launchable_activity)


if __name__ == '__main__':
    r = getApkInfo(
        "/Users/zhimingwu/PycharmProjects/TestingPlatform/media/app/KeruyunCalm3_V8.15.0_CI_B1abcba52_180730134119.apk")
    print(r)
