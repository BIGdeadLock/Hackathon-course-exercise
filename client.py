import socket
import struct
from offer import OfferPacket
import scapy.all as scapy


serverName='serverName'
#server_port = 13117
server_port = 13000
Client = socket.socket(); 
Client.connect(("172.1.0.42", 13000))
# Listen for broadcast of UDP from the server
sentence = print('Client started, listening for offer requests...')
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) 
client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

# Enable broadcasting mode
client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

payload_size = OfferPacket.payload_size
local_ip = scapy.get_if_addr("eth1")

client.bind(("", server_port))
while True:
    data, addr = client.recvfrom(1024)
    if len(data) < payload_size:
        if not data:
            # client closed after last message, assume all is well
            print("Client Closed")
        else:
            # raise IOError("Truncated message")
            print("Truncated message")
            continue



    if not OfferPacket.validate_packet(data):
        print("Recieved a message which is not an offer message. Please try sending again")
    
    port = OfferPacket.get_port_from_data(data)
    print(port)
    print(f"Received offer from {addr[0]}, attempting to connect...")
    Clinet = socket.socket(); 
    Clinet.connect((addr[0], port))

    

# clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# clientSocket.listen(server_port)
# clientSocket.connect((serverName, server_port))
# clientSocket.send(sentence)
# modifiedSentence = clientSocket.recv(1024)
# print('from Server:',modifiedSentence)
# clientSocket.close()

