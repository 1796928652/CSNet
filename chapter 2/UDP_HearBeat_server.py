from socket import *
import random
import time

serverSocket = socket(AF_INET, SOCK_DGRAM)
serverPort = 12000
serverSocket.bind(('', serverPort))

startTime = float(time.time())
endTime = startTime

while True:
    try:
        serverSocket.settimeout(0.1)
        message, address = serverSocket.recvfrom(1024)
        message = message.decode()
        rtime = float(message.split()[1])
        endTime = rtime
        Ping = float(time.time()) - rtime
        print(str(message.split()[0]) + ':' + str(Ping))
    except Exception as e:
        if endTime == startTime:
            continue
        if time.time() - endTime > 1.0:
            print('HearBeat server pause')
            break
        else:
            print('Packet lost')
