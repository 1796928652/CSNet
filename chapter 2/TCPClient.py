from socket import *


serverName = '10.8.195.104'  #服务器IP地址
serverPort = 12000  #服务器端口号

clientSocket = socket(AF_INET, SOCK_STREAM)  #采用IP_V4协议 与 进行TCP连接
clientSocket.connect((serverName, serverPort))  #客户端需要连接的服务器地址与对应的端口号
message = input("Enter your message: ")
clientSocket.send(message.encode())
modifiedMessage = clientSocket.recv(1024)
print('From Server:', modifiedMessage.decode())
