import struct

def send_message(sock, message):
    encoded = message.encode()
    length = struct.pack('!I', len(encoded))
    sock.sendall(length + encoded)

def recv_message(sock):
    raw_len = recv_all(sock, 4)
    if not raw_len:
        return None
    msg_len = struct.unpack('!I', raw_len)[0]
    return recv_all(sock, msg_len).decode()

def recv_all(sock, n):
    data = b''
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data += packet
    return data