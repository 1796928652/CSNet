# sender.py - The sender in the reliable data transfer protocol
import json
import socket
import threading
import udt
import time
from packet import *
import rsa
#   滑动窗口大小
window_size = 4
# 上层数据（文件）打包成数据包存入 packet_list 中
packet_list = []
base = 0
TIMEOUT_INTERVAL = 0.01


class Client:

    def __init__(self, server_ip, server_port, window, client_pkt_port, filename):
        global packet_list
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

        # Open the file
        try:
            file = open(filename, 'rb')
            content = file.read()
            packet_list = make_packet_List(content=content, filename=filename)
        except IOError:
            print('Unable to open', filename)
            return

    def set_window_size(self):
        global packet_list
        global base
        return min(window_size, len(packet_list) - base)

    def re_send(self, num):
        global packet_list
        print('Resending packet ' + str(num))
        udt.send(packet_list[num], self.send_socket, self.server_address)

    def run(self, num):
        global base
        time.sleep(TIMEOUT_INTERVAL)
        while num > base:
            self.re_send(num)
            time.sleep(TIMEOUT_INTERVAL)
        self.timers.pop(num)


    def send(self):
        global base
        global window_size
        global packet_list
        next_to_send = 0
        #   先设置一个window_size 防止数据包数量很小 以至于小过预设定的window_size
        window_size = self.set_window_size()
        print('pkt_list: ' + str(len(packet_list)))
        while base < len(packet_list) - 1:
            window_size = self.set_window_size()
            while next_to_send < base + window_size:
                print('Sending packet', next_to_send)
                '''
                try:
                    udt.send(packet_list[next_to_send], self.send_socket, self.server_address)
                except IndexError:
                    print('next_to_send,', next_to_send, 'base', base, 'window_size', window_size)
                '''
                udt.send(packet_list[next_to_send], self.send_socket, self.server_address)
                #   给每个需要回应的ack序列号代表的数据包设置一个重发线程 并且公开允许访问ack_list 以判断自身的数据包是否交付给接收方
                receive_ack = threading.Thread(target=self.run, args=(next_to_send,))
                receive_ack.start()
                self.timers[next_to_send] = receive_ack
                next_to_send += 1
                if next_to_send == len(packet_list):
                    return

    def receive(self):
        global base
        global window_size
        global packet_list
        dupACKcount = 0
        while base < len(packet_list) - 1:
            data, addr = udt.recv(self.ack_socket)
            data = json.loads(data.decode('utf-8'))
            print('Received', data['pkt_type'], data['number'])
            if check_ack(data):
                #   检查是否为冗余ACK
                if data['pkt_type'] == 'DupAck_pkt':
                    dupACKcount += 1
                else:
                    # if ack's num > base updata the base and dupAckCOUNT
                    if base < data['number']:
                        base = data['number']
                        dupACKcount = 0
            if dupACKcount >= 3:
                print('Trigger Fast Retransmission')
                udt.send(packet_list[base], self.send_socket, self.server_address)
                dupACKcount = 0
            if base == len(packet_list) - 1:
                base += 1



if __name__ == '__main__':
    print('Sender ready')
    filename = r"C:\Users\WangJinjie\Desktop\新建文件夹\基础练习\基础练习要求.docx"
    c = Client(server_ip=socket.gethostbyname(socket.gethostname()), server_port=8080, window=window_size,
               client_pkt_port=8888, filename=filename)
    thread_send = threading.Thread(target=c.send)
    thread_receive = threading.Thread(target=c.receive)
    thread_send.start()
    thread_receive.start()
    thread_send.join()
    thread_receive.join()
    print('Send done')
