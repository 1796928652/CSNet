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

    def Is_Complete_pkt_list(self):
        global pkt_list
        j = 0
        for i in pkt_list:
            if i['number'] == j:
                j += 1
            else:
                return False
        return True

    def receive(self, num_for_file: int):
        global expected_pkt, pkt_buffer, pkt_list
        expected_pkt = 0
        pkt_buffer = []
        pkt_list = []
        while True:
            data, addr = udt.recv(self.server_socket)
            #   规定过客户端的接收ACK的端口为 客户端的发送端口+5
            client_addr = (addr[0], addr[1] + 5)
            temp = getdict(data)
            if checkSumVerification(data):
                print('Receive', temp['number'])
                if temp['number'] == expected_pkt:
                    pkt_list.append(getdict(data))
                    #   send ack
                    ackpkt = createAck(temp['number'])
                    udt.ACK_send(ackpkt, self.ack_socket, client_addr)
                    # When the smallest seq_num pkt get
                    # Clear the buffer
                    pkt_buffer.append(expected_pkt)
                    pkt_buffer.sort()
                    while pkt_buffer and pkt_buffer[0] == expected_pkt:
                        expected_pkt += 1
                        pkt_buffer.remove(pkt_buffer[0])
                        pkt_buffer.sort()
                #   注意这里关于temp['number']的条件判断必须这么写 如果有上一个文件残余的序列号数据的ACK没回复的话 维系这个滑动窗口可以大大过滤掉上一个文件的数据序列号而不会和本次数据相干扰
                #              可以考虑的是 在极端条件下 ->如果上一个文件的序列号数据包的ACK刚好一直没有得以交给发送方 一直拖到下一个文件的滑动窗口内 那么可能会发生碰撞
                #                   当然 必须指出的是 极端条件很难成立 在丢包率为p的情况下 极端条件成立的可能大约为  （p）^（文件打包成数据的大小-滑动窗口大小）
                #                   解决极端条件的方案 最直接有效的就是重新传输一遍
                elif temp['number'] < expected_pkt:
                    ackpkt = createAck(expected_pkt - 1)
                    udt.ACK_send(ackpkt, self.ack_socket, client_addr)
                elif expected_pkt < temp['number'] < WINDOW_SIZE + expected_pkt:
                    if temp['number'] not in pkt_buffer:
                        pkt_buffer.append(temp['number'])
                        pkt_buffer.sort()
                        pkt_list.append(getdict(data))
                    # send dupACK
                    DupAck_pkt = createDupAck(expected_pkt)
                    udt.ACK_send(DupAck_pkt, self.ack_socket, client_addr)
                '''
                #   防止上一个文件的最后一份数据没有传完而发送端始终无法关闭
                else:
                    ackpkt = createAck(temp['number'])
                    udt.ACK_send(ackpkt, self.ack_socket, client_addr)
                #   注意上次这样写似乎有些许问题 有可能对发送方产生 意外地大大提高了base 而导致一些小于base的pkt无法传输的问题 
                    但仍要解决上一份文件最后的pkt传输完后反馈问题
                    现实中考虑到 发送文件到接收端为第一需求 而对于 防止上一个文件的最后一份数据没有传完而发送端始终无法关闭这样的问题是次要的
                        现实中也不会多次传输同一个文件 所以我们可以提取文件的某个特征作为他的标识 以应对上一份文件未传完的问题
                        如果这个特征仍然是上一份文件的特征那么接收端做出一个回应而不接收该pkt
                        如果这个特征不是上一份文件的特征那么接收端如期工作
                    解决思路是我们设置一个时间如果
                '''
            pkt_list = sorted(pkt_list, key=lambda k: k['number'])
            # 可能先收到最后一个close_pkt 但回复的ACK由于意外没有传递给发送方而导致发送方一直传输close_pkt 所以接受方不能着急关闭 而是要确定最后一项ACK确实交付给发送方
            # 其实也可以接收方一直不关闭   保持默认接收的状态   如果接收到确认完整收到整个pkt 则交付上层 接收方保持默认接收状态
            # 如果发送方上一个文件的最后一个分组没有收到对应的ACK而不断发送该分组，那么由于接收方一直保持打开状态则可以对发送方的上一个文件的最后几个分组回应ACK 上面的else即相应的代码块
            if pkt_list and pkt_list[-1]['pkt_type'] == 'close_pkt':
                #   由于close_pkt可能先一步抵达 所有仍需判断pkt_list的完整性
                if self.Is_Complete_pkt_list():
                    with open(str(num_for_file) + 'text.txt', 'wb') as file:
                        for i in pkt_list:
                            if i['pkt_type'] == 'data_pkt':
                                file.write(bytes(i['data']))
                    break


if __name__ == '__main__':
    num_for_file = 1
    while True:
        print('Receive ready')
        r = Server(server_ip=socket.gethostbyname(socket.gethostname()), server_port=8080)
        r.receive(num_for_file)
        print(num_for_file, 'File Receive done')
        num_for_file += 1
