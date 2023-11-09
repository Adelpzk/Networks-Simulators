import socket
import struct

DNS_RECORDS = {
    'google.com': [('192.165.1.1', 260), ('192.165.1.10', 260)],
    'youtube.com': [('192.165.1.10', 160)],
    'uwaterloo.ca': [('192.165.1.3', 160)],
    'wikipedia.org': [('192.165.1.4', 160)],
    'amazon.ca': [('192.165.1.5', 160)]
}

SERVER_IP = '127.0.0.1'
SERVER_PORT = 10500

# parse the query received from client
def parse_query(data):
    transaction_id, flags, qdcount = struct.unpack('>HHH', data[:6])
    
    pointer = 12
    domain_parts = []
    while True:
        length = data[pointer]
        if length == 0:
            pointer += 1
            break
        domain_parts.append(data[pointer + 1:pointer + 1 + length])
        pointer += 1 + length
    domain_name = b'.'.join(domain_parts).decode()

    return transaction_id, domain_name

#make the response to be sent back to the client
def create_response(transaction_id, domain_name):
    if domain_name in DNS_RECORDS:
        flags = 0x8400  
        qdcount = 1
        ancount = len(DNS_RECORDS[domain_name])
        nscount = 0
        arcount = 0
        header = struct.pack('>HHHHHH', transaction_id, flags, qdcount, ancount, nscount, arcount)

        question = b''
        for part in domain_name.split('.'):
            question += struct.pack('B', len(part)) + part.encode()
        question += struct.pack('BHB', 0, 1, 1) 
        
        answer = b''
        for ip, ttl in DNS_RECORDS[domain_name]:
            answer += struct.pack('>HHHLH4s', 0xC00C, 1, 1, ttl, 4, socket.inet_aton(ip))

        return header + question + answer
    else:
        return b''

def print_hex(data):
    print(" ".join(f"{b:02x}" for b in data))

def run_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((SERVER_IP, SERVER_PORT))

    try:
        while True:
            data, addr = server_socket.recvfrom(512)
            print("Request:")
            print_hex(data)
            transaction_id, domain_name = parse_query(data)
            response = create_response(transaction_id, domain_name)
            print("Response:")
            print_hex(response)
            server_socket.sendto(response, addr)
    finally:
        server_socket.close()

if __name__ == '__main__':
    run_server()







    