# receiver.py - The receiver in the reliable data transer protocol(SR)
import hashlib

from packet import *
import socket
import random
import udt

#   pkt_buffer为缓冲区
global expected_pkt, curr_pkt, pkt_buffer, pkt_list
import threading

#   维系滑动窗口 但实际上这个滑动窗口在接收方中只用作于判定上一个文件的残余ACK是否未回复
WINDOW_SIZE = 4

class Server:

    def __init__(self, server_ip, server_port):
        self.server_ip = server_ip
        self.server_port = server_port
        self.ack_port = server_port + 5

        server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(('', self.server_port))
        self.server_socket = server_socket

        ack_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        ack_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        ack_socket.bind(('', self.ack_port))
        self.ack_socket = ack_socket

    def receive(self, num_for_file: int):
        global expected_pkt, curr_pkt, pkt_buffer, pkt_list
        expected_pkt = 0
        curr_pkt = 0
        pkt_buffer = []
        pkt_list = []
        while True:
            #   data, addr = self.server_socket.recvfrom(1024)
            data, addr = udt.recv(self.server_socket)
            #   规定过客户端的接收ACK的端口为 客户端的发送端口+5
            client_addr = (addr[0], addr[1] + 5)
            temp = getdict(data)
            if checkSumVerification(data):
                ackpkt = createAck(temp['number'])
                print('Receive', temp['number'])
                udt.ACK_send(ackpkt, self.ack_socket, client_addr)
                if temp['number'] == expected_pkt:
                    expected_pkt += 1
                    curr_pkt = temp['number']
                    pkt_list.append(getdict(data))
                    # When the smallest seq_num pkt get
                    # Clear the buffer
                    while pkt_buffer and pkt_buffer[0] == expected_pkt:
                        curr_pkt = expected_pkt
                        expected_pkt += 1
                        pkt_buffer.remove(pkt_buffer[0])
                        pkt_buffer.sort()
                #   注意这里关于temp['number']的条件判断必须这么写 如果有上一个文件残余的序列号数据的ACK没回复的话 维系这个滑动窗口可以大大过滤掉上一个文件的数据序列号而不会和本次数据相干扰
                #              可以考虑的是 在极端条件下 ->如果上一个文件的序列号数据包的ACK刚好一直没有得以交给发送方 一直拖到下一个文件的滑动窗口内 那么可能会发生碰撞
                #                   当然 必须指出的是 极端条件很难成立 在丢包率为p的情况下 极端条件成立的可能大约为  （p）^（文件打包成数据的大小-滑动窗口大小）
                #                   解决极端条件的方案 最直接有效的就是重新传输一遍
                elif expected_pkt < temp['number'] < WINDOW_SIZE + expected_pkt and temp['number'] not in pkt_buffer:
                    pkt_list.append(getdict(data))
                    pkt_buffer.append(temp['number'])
                    pkt_buffer.sort()

            pkt_list = sorted(pkt_list, key=lambda k: k['number'])
            #   可能先收到最后一个close_pkt 但回复的ACK由于意外没有传递给发送方而导致发送方一直传输close_pkt
            #   所以接受方不能着急关闭 而是要确定最后一项ACK确实交付给发送方
            #   其实也可以接收方一直不关闭   保持默认接收的状态   如果接收到确认完整收到整个pkt 则交付上层
            print('len(pkt_list)', len(pkt_list))
            if pkt_list and pkt_list[-1]['number'] == len(pkt_list)-1 and pkt_list[-1]['pkt_type'] == 'close_pkt':
                with open(str(num_for_file)+'text.txt', 'wb') as file:
                    for i in pkt_list:
                        if i['pkt_type'] == 'data_pkt':
                            file.write(bytes(i['data']))
                #   重新归零    以待下一个文件的传输
                #   这里由于回复的ACK没有抵达而导致发送方一直在发送没有回复的ACK所以设置一个Finall_pkt
                break


if __name__ == '__main__':
    num_for_file = 1
    while True:
        print('Receive ready')
        r = Server(server_ip= socket.gethostbyname(socket.gethostname()), server_port=8080)
        r.receive(num_for_file)
        print(num_for_file, 'File Receive done')
        num_for_file += 1
