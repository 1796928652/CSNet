from socket import *
import random

#Create a UDP socket
serverSocket = socket(AF_INET, SOCK_DGRAM)

#Assign IP address and port number to socket
serverSocket.bind(('', 12000))

#服务器程序在一个无限循环中监听到来的UDP数据包。当数据包到来时，随机生成一个0到10的数 如果大于等于4则将收到的数据大写并返回给client
## 为什么要随机生成一个0到10的数？   UDP为应用程序提供了不可靠的传输服务。消息可能因为路由器队列溢出，硬件错误或其他原因，而在网络中丢失。但由于在内网中很丢包甚至不丢包，所以在本实验室的服务器程序添加人为损失来模拟网络丢包的影响。服务器创建一个随机整数，由它确定传入的数据包是否丢失。
###                            因为我们想要模拟有30%的来自client的丢包率
while True:
    #Generate random number in the range of 0 to 10
    rand = random.randrange(0, 10)

    #Receive the client packet along with the address it is coming from
    message, address = serverSocket.recvfrom(1024)

    #Capitalize the message from the client
    message = message.upper()

    #If rand is less than 4, we consider the packet lost and not respond
    if rand < 4:
        continue
    #otherwise , the server responds
    serverSocket.sendto(message, address)
