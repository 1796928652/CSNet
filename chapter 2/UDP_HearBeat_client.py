from socket import *
import time

serverName = '10.8.195.104'
serverPort = 12000
clientSocket = socket(AF_INET, SOCK_DGRAM)
for i in range(0, 10):
    start = time.time()
    message = str(i) + ' ' + str(time.time())
    clientSocket.sendto(message.encode(), (serverName, serverPort))
clientSocket.close()