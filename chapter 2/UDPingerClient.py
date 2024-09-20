from socket import *
import time

serverName = '10.8.195.104'
serverPort = 12000
clientSocket = socket(AF_INET, SOCK_DGRAM)
clientSocket.settimeout(1)  #设置套接字超时值为1秒

minRTT = float("inf")
maxRTT = float("-inf")
averageRTT = 0
LossCounter = 0

for i in range(0, 10):
    sendTime = time.time()
    message = ('Ping %d %s' % (i + 1, sendTime)).encode()
    try:
        clientSocket.sendto(message, (serverName, serverPort))
        modifiedMessage, serverAddress = clientSocket.recvfrom(2048)
        RTT = time.time() - sendTime  #计算RTT
        minRTT = min(RTT, minRTT)
        maxRTT = max(RTT, maxRTT)
        averageRTT += RTT
        print('Sequence %d: Relay from %s   RTT= %.5fs' % (i + 1, serverAddress, RTT))
    except Exception as e:
        LossCounter += 1
        print('Sequence %d: Request timed out' % (i + 1))
clientSocket.close()

5
averageRTT = averageRTT / 10
lossCounter = LossCounter / 10
print('minRTT: %.3fs' % minRTT)
print('maxRTT: %.3fs' % maxRTT)
print('Average RTT: %.3fs' % averageRTT)
print('Loss counter: %.3f' % LossCounter)