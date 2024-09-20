from socket import *

serverPort = 12000
serverSocket = socket(AF_INET, SOCK_STREAM)     #欢迎套接字
serverSocket.bind(('', serverPort))
serverSocket.listen(1)
print('waiting for a connection')
while True:
    connectionSocket, addr = serverSocket.accept()      #与用户进行连接的套接字
    print('Got connection from', addr)
    data = connectionSocket.recv(1024).decode()
    print('From client:', data)
    connectionSocket.send(data.upper().encode())
    connectionSocket.close()
