from socket import *

serverPort = 12001
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(('', serverPort))
serverSocket.listen(1)
print('waiting for a connection')

while True:
    print('Ready to serve')
    connectionSocket, addr = serverSocket.accept()
    try:
        message = connectionSocket.recv(1024).decode()  # 获取客户发送的报文 并且编码为str类型
        filename = message.split()[1]   #切割字符串 得到url字段
        print(filename[1:])     #取文件名
        f = open(filename[1:])  #打开文件
        outputdata = f.read();
        print(outputdata)
        # Send one HTTP header line into socket
        header = ' HTTP/1.1 200 OK\nConnection: close\nContent-Type: text/html\nContent-Length: %d\n\n' % (
            len(outputdata))
        connectionSocket.send(header.encode())

        # Send the content of the requested file to the client
        connectionSocket.send(outputdata.encode())
        connectionSocket.close()
    except IOError:
        #Send response message for file not found
        header = 'HTTP/1.1 404 Not Found'
        connectionSocket.send(header.encode())

        #Close the socket
        connectionSocket.close()

serverSocket.close()
