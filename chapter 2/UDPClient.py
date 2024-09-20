from socket import *

serverName= gethostbyname(gethostname())
serverPort = 12000
clientSocket = socket(AF_INET, SOCK_DGRAM)
message = input("Enter your message: ")
clientSocket.sendto(message.encode(), (serverName, serverPort))
modifiedMessage, serverAddress = clientSocket.recvfrom(2048)
print(modifiedMessage.decode())
clientSocket.close()

