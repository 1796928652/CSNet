# Creates a packet from a sequence number and byte data
import json
import hashlib


def jsonify(data, pkt_type, number, status, csum):
    pkt_dict = {
        'data': list(data),
        'pkt_type': pkt_type,
        'number': number,
        'status': status,
        'checksum': csum
    }
    pkt_json = json.dumps(pkt_dict).encode('utf-8')
    return pkt_json


def getdict(pkt):
    return json.loads(pkt.decode('utf-8'))


# set checksum
def checksum(data, pkt_type, number, status):
    hash_str = str(data) + '.' + pkt_type + '.' + str(number) + '.' + str(status)
    return hashlib.md5(hash_str.encode('utf-8')).hexdigest()


# Verificate the chesksum
def checkSumVerification(pkt):
    currpkt = json.loads(pkt.decode('utf-8'))
    data = bytes(currpkt['data'])
    pkt_type = currpkt['pkt_type']
    number = currpkt['number']
    status = currpkt['status']

    if checksum(data, pkt_type, number, status) == currpkt['checksum']:
        return True
    else:
        return False


def make_packet_List(content, filename):
    packet_list = []
    num = 0
    while len(content) != 0:
        data = content[0:64]
        num += 1
        csum = checksum(data, 'data_pkt', number=num - 1, status=False)
        data = jsonify(data, pkt_type='data_pkt', number=num - 1, status=False, csum=csum)
        packet_list.append(data)
        content = content[64:]

    num += 1
    bye = 'Bye'
    data = bytes(bye, 'utf-8')
    csum = checksum(data, 'close_pkt', number=num - 1, status=False)
    data = jsonify(data, pkt_type='close_pkt', number=num - 1, status=False, csum=csum)
    packet_list.append(data)
    return packet_list


def createAck(data_num):
    data = 'Ack Sent'
    data = bytes(data, 'utf-8')
    csum = checksum(data, 'ack_pkt', number=data_num, status=True)
    ackpkt = jsonify(data, 'ack_pkt', number=data_num, status=True, csum=csum)
    return ackpkt


def check_ack(pkt):
    ack_data = bytes(pkt['data'])
    if checksum(ack_data, pkt['pkt_type'], pkt['number'], pkt['status']) == pkt['checksum']:
        return True
    else:
        return False


def finish():
    data = 'finish'
    data = bytes(data, 'utf-8')
    csum = checksum(data, 'finish_pkt', number=-1, status=False)
    finish_pkt = jsonify(data, 'finish_pkt', number=-1, status=False, csum=csum)
    return finish_pkt