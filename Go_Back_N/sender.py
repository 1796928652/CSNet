# sender.py - The sender in the reliable data transfer protocol
import packet
import socket
import sys
import _thread
import time
import udt

from timer import Timer

PACKET_SIZE = 512
RECEIVER_ADDR = (socket.gethostbyname(socket.gethostname()), 8080)
SENDER_ADDR = (socket.gethostbyname(socket.gethostname()), 0)
SLEEP_INTERVAL = 0.05
#   timeout_interval对应Timer类中的duration
TIMEOUT_INTERVAL = 0.05
WINDOW_SIZE = 4

# Shared resources across threads
#   base为基序号
base = 0
#   分配一个锁对象，用于同步多个线程的访问
mutex = _thread.allocate_lock()

send_timer = Timer(TIMEOUT_INTERVAL)


# Sets the window size
# num_packets 为将文件切片后切片的个数
# 一般来说 切片个数会大于窗口长度 但万一窗口长度大于切片个数呢？
def set_window_size(num_packets):
    global base
    return min(WINDOW_SIZE, num_packets - base)


# Send thread
def send(sock, filename):
    global mutex
    global base
    global send_timer

    # Open the file
    try:
        file = open(filename, 'rb')
    except IOError:
        print('Unable to open', filename)
        return

    # Add all the packets to the buffer
    packets = []
    seq_num = 0
    while True:
        data = file.read(PACKET_SIZE)
        if not data:
            break
        packets.append(packet.make(seq_num, data))
        seq_num += 1

    num_packets = len(packets)
    print('I gots', num_packets)
    window_size = set_window_size(num_packets)
    next_to_send = 0
    base = 0

    # Start the receiver thread
    # _thread.start_new_thread(function, args[, kwargs])：创建一个新的线程，并开始执行指定的函数(
    # 这里为receiver)。function 是线程将要执行的函数，args 是传递给该函数的参数元组，kwargs 是可选的关键字参数字典
    # 启动一个名为receive的线程
    _thread.start_new_thread(receive, (sock,))

    while base < num_packets:
        mutex.acquire()
        # Send all the packets in the window
        while next_to_send < base + window_size:
            print('Sending packet', next_to_send)
            udt.send(packets[next_to_send], sock, RECEIVER_ADDR)
            next_to_send += 1

        # Start the timer
        if not send_timer.running():
            print('Starting timer')
            send_timer.start()

        # Wait until a timer goes off or we get an ACK
        while send_timer.running() and not send_timer.timeout():
            mutex.release()
            print('Sleeping')
            time.sleep(SLEEP_INTERVAL)
            mutex.acquire()

        if send_timer.timeout():
            # Looks like we timed out
            print('Timeout')
            send_timer.stop()
            next_to_send = base
        else:
            print('Shifting window')
            window_size = set_window_size(num_packets)
        mutex.release()

    # Send empty packet as sentinel
    udt.send(packet.make_empty(), sock, RECEIVER_ADDR)
    file.close()


# Receive thread
def receive(sock):
    global mutex
    global base
    global send_timer

    while True:
        pkt, _ = udt.recv(sock)
        #   提取出对应的序号 为ack
        ack, _ = packet.extract(pkt)

        # If we get an ACK for the first in-flight packet
        print('Got ACK', ack)
        #   GBN采用的是累积确认 所以只要有一个序号ack大于base即可确认ack之前的所有分组都抵达
        if (ack >= base):
            mutex.acquire()
            base = ack + 1
            print('Base updated', base)
            send_timer.stop()
            mutex.release()


# Main function
if __name__ == '__main__':
    '''
    if len(sys.argv) != 2:
        print('Expected filename as command line argument')
        exit()
    '''
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(SENDER_ADDR)
    filename = r"C:\Users\WangJinjie\Desktop\新建文件夹\B题数据\B题 气候对粮食安全及农业可持续发展的影响研究.doc"    #   sys.argv[1]

    send(sock, filename)
    sock.close()
