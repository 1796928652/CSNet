from socket import *


request_head_1='GET /'
request_head_2=' HTTP/1.1\nHost: 10.8.195.104\nConnection: keep-alive\nUpgrade-Insecure-Requests: 1\n\
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3\n\
Purpose: prefetch\n\
Accept-Encoding: gzip, deflate, br\n\
Accept-Language: zh-CN,zh;q=0.9,en;q=0.8'
filename='HelloWorld.html'
request_head=request_head_1+filename+request_head_2


serverAddr = ('10.8.195.104', 12001)

clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect(serverAddr)

clientSocket.send(request_head.encode())
for i in range(2):
    mod=clientSocket.recv(1024)
    print(mod.decode())
clientSocket.close()

