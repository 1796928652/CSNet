# sender.py - The sender in the reliable data transfer protocol
import json
import socket
import threading
import udt
import time
from packet import *

#   滑动窗口大小
window_size = 4
# 上层数据（文件）打包成数据包存入 packet_list 中
packet_list = []
base = 0
TIMEOUT_INTERVAL = 0.01
#   发送方眼中 接受到的ack序列表 在其中的ack为未接收到的序列号 也就是需要重传处理的
ack_list = []


class Client:

    def __init__(self, server_ip, server_port, window, client_pkt_port):

        self.server_ip = server_ip
        self.server_port = server_port
        self.window = window
        self.pkt_port = client_pkt_port
        self.ack_port = client_pkt_port + 5
        self.server_address = (self.server_ip, self.server_port)

        send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        send_socket.bind(('', client_pkt_port))
        self.send_socket = send_socket

        ack_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        ack_socket.bind(('', self.ack_port))
        self.ack_socket = ack_socket

        self.timers = {}

    def set_window_size(self):
        global packet_list
        global base
        return min(window_size, len(packet_list) - base)

    def re_send(self, num):
        global packet_list
        print('Resending packet ' + str(num))
        #   self.send_socket.sendto(packet_list[num], self.server_address)
        udt.send(packet_list[num], self.send_socket, self.server_address)

    def run(self, num):
        global packet_list
        global ack_list
        time.sleep(TIMEOUT_INTERVAL)
        while num in ack_list:
            self.re_send(num)
            time.sleep(TIMEOUT_INTERVAL)

    def send(self, filename):
        global packet_list
        global base
        global window_size
        global ack_list
        # Open the file
        try:
            file = open(filename, 'rb')
            content = file.read()
            packet_list = make_packet_List(content=content, filename=filename)
            ack_list = [i for i in range(len(packet_list))]
        except IOError:
            print('Unable to open', filename)
            return

        next_to_send = 0
        window_size = self.set_window_size()
        #   发送方的目的为 消除ack_list中所有元素
        while ack_list:
            #   先设置一个window_size 防止数据包数量很小 以至于小过预设定的window_size
            window_size = self.set_window_size()

            while next_to_send < base + window_size:
                print('Sending packet', next_to_send)
                #   self.send_socket.sendto(packet_list[next_to_send], self.server_address)
                udt.send(packet_list[next_to_send], self.send_socket, self.server_address)
                #   给每个需要回应的ack序列号代表的数据包设置一个重发线程 并且公开允许访问ack_list 以判断自身的数据包是否交付给接收方
                receive_ack = threading.Thread(target=self.run, args=(next_to_send,))
                receive_ack.start()
                self.timers[next_to_send] = receive_ack
                next_to_send += 1

            #   data, addr = self.ack_socket.recvfrom(1024)
            data, addr = udt.recv(self.ack_socket)
            data = json.loads(data.decode('utf-8'))
            print('Received ACK', data['number'])
            if check_ack(data):
                ack_list.remove(data['number'])

            # 注意 base表示的是index 所以得小于数据包数量
            while base < len(packet_list) and base not in ack_list:
                self.timers.pop(base)
                base += 1


if __name__ == '__main__':
    print('Sender ready')
    filename = r"C:\Users\WangJinjie\Desktop\新建文件夹\基础练习\基础练习要求.docx"
    c = Client(server_ip=socket.gethostbyname(socket.gethostname()), server_port=8080, window=window_size, client_pkt_port=8888)
    c.send(filename=filename)
    print('Send done')
