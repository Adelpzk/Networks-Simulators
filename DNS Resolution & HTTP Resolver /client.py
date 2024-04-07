import random
import socket
import struct
import sys

DNS_RECORDS = {
    'google.com': [('192.165.1.1', 260), ('192.165.1.10', 260)],
    'youtube.com': [('192.165.1.10', 160)],
    'uwaterloo.ca': [('192.165.1.3', 160)],
    'wikipedia.org': [('192.165.1.4', 160)],
    'amazon.ca': [('192.165.1.5', 160)]
}

def create_dns_query(domain):
    # Generates a random ID for the query
    transaction_id = random.randint(0, 255)

    flags = 0
    
    # Set AA (bit 10)
    flags |= (1 << 10)
   
    qdcount = 1
    
    ancount = nscount = arcount = 0
    
    header = struct.pack('>HHHHHH', transaction_id, flags, qdcount, ancount, nscount, arcount)
    
    qname = b''.join(len(part).to_bytes(1, 'big') + part.encode() for part in domain.split('.'))
    
    # Final null byte to the domain name
    qname += b'\x00'
    
    qtype = 1
    
    qclass = 1
    
    question = struct.pack(f'>{len(qname)}sHH', qname, qtype, qclass)
    
    return header + question

def print_hex(data):
    print(" ".join(f"{b:02x}" for b in data))

def main():
    while (1):
        domain = input("Enter Domain Name: ")
        
        
        if domain.lower() == 'end':
            print('Session ended')
            return
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_address = ('127.0.0.1', 10500)
        if (domain not in DNS_RECORDS):
            print('Invalid Domain Name')
            sock.sendto(b'', server_address)
            continue
    
        query = create_dns_query(domain)
        
        sock.sendto(query, server_address)

        response, _ = sock.recvfrom(512) 

        header_length = 12
        question_length = response[header_length:].index(0) + 5
        answer_section_start = header_length + question_length

        # Range is 2 since google has 2 ip addresses
        answers = []
        for i in range(2):  # two answers
            answer_start = answer_section_start + i * 16
            answer = response[answer_start:answer_start + 12]
            if (answer == b''):
                continue
            _, type_, class_, ttl, rdlength = struct.unpack('>HHHLH', answer)
            
            rdata_start = answer_start + 12
            rdata = response[rdata_start:rdata_start + rdlength]

            ip_address = socket.inet_ntoa(rdata)
    
            answers.append((type_, class_, ttl, rdlength, ip_address))

        for answer in answers:
            type_, class_, ttl, rdlength, ip_address = answer
            type_str = 'A' if type_ == 1 else 'Unknown'
            class_str = 'IN' if class_ == 1 else 'Unknown'
            print(f"{domain}: type {type_str}, class {class_str}, TTL {ttl}, addr ({rdlength}) {ip_address}")

if __name__ == '__main__':
    main()