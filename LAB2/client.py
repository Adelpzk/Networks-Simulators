import random
import socket
import struct
import sys

def create_dns_query(domain):
    # Generate a random ID for the query
    transaction_id = random.randint(0, 255)

    # Initial flags set to 0
    flags = 0

    # Set AA (bit 10)
    # For an authoritative answer
    flags |= (1 << 10)
   
    # Question Count: 1
    qdcount = 1
    
    # Answer Count, Name Server Count, Additional Records Count: 0
    ancount = nscount = arcount = 0
    
    # Create the DNS Header
    header = struct.pack('>HHHHHH', transaction_id, flags, qdcount, ancount, nscount, arcount)
    
    # Create the DNS Question
    # Split the domain by '.', prepend length of each part
    qname = b''.join(len(part).to_bytes(1, 'big') + part.encode() for part in domain.split('.'))
    
    # Add the final null byte to the domain name
    qname += b'\x00'
    
    # Type A (host address)
    qtype = 1
    
    # Class IN (Internet)
    qclass = 1
    
    # Pack the question fields
    question = struct.pack(f'>{len(qname)}sHH', qname, qtype, qclass)
    
    # Return the query
    return header + question

def print_hex(data):
    print(" ".join(f"{b:02x}" for b in data))

def main():
    while (1):
        domain = input("Enter Domain Name: ")
    
        if domain.lower() == 'end':
            print('Session ended')
            return
    
        query = create_dns_query(domain)
    
        # The following lines would be used to send the query to the server
        # For now, we will just print the query
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_address = ('127.0.0.1', 10500) # replace 53 with your chosen port
        sock.sendto(query, server_address)

        # Here you would receive the response from the server and process it
        response, _ = sock.recvfrom(512) # 512 is a safe value for the buffer size

        header_length = 12
        question_length = response[header_length:].index(0) + 5  # +5 for QTYPE and QCLASS
        answer_section_start = header_length + question_length

        # There are two answers in this response, so we'll loop twice
        answers = []
        for i in range(2):  # two answers
            # Each answer is 16 bytes long, but we'll extract RDATA separately due to its variable length
            answer_start = answer_section_start + i * 16
            answer = response[answer_start:answer_start + 12]
            if (answer == b''):
                continue
            _, type_, class_, ttl, rdlength = struct.unpack('>HHHLH', answer)
            
            # Calculate the start of the RDATA field and extract it
            rdata_start = answer_start + 12
            rdata = response[rdata_start:rdata_start + rdlength]

            # Convert RDATA to an IP address
            ip_address = socket.inet_ntoa(rdata)
    
            # Append to the list of answers
            answers.append((type_, class_, ttl, rdlength, ip_address))

        # Print the results
        for answer in answers:
            type_, class_, ttl, rdlength, ip_address = answer
            type_str = 'A' if type_ == 1 else 'Unknown'
            class_str = 'IN' if class_ == 1 else 'Unknown'
            print(f"{domain}: type {type_str}, class {class_str}, TTL {ttl}, addr ({rdlength}) {ip_address}")

if __name__ == '__main__':
    main()