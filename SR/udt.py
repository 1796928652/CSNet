# Due to testing in local host, we have to simulate real packet loss
import random
import socket

DROP_PROB = 100
Pass_Prob = 10


# Send a packet across the unreliable channel
# In order to statistics the number of loss, we need to return int
def send(packet, sock, addr):
    if random.randint(0, DROP_PROB) > Pass_Prob:
        sock.sendto(packet, addr)
        return 0
    else:
        print('Send failure')
        return 1


def ACK_send(packet, sock, addr):
    if random.randint(0, DROP_PROB) > Pass_Prob:
        sock.sendto(packet, addr)
        return 0
    else:
        print('ACK  failure')
        return 1


# Receive a packet from the unreliable channel
def recv(sock):
    packet, addr = sock.recvfrom(1024)
    return packet, addr
