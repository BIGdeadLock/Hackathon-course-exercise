import socket
import struct
from offer import OfferPacket

serverName='serverName'
server_port = 13117


# Listen for broadcast of UDP from the server
sentence = print('Client started, listening for offer requests...')
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) 
client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

# Enable broadcasting mode
client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
payload_size = struct.calcsize("Ibh")

client.bind(("", server_port))
while True:
    data, addr = client.recvfrom(1024)
    if len(data) < payload_size:
        if not data:
            # client closed after last message, assume all is well
            print("Client Closed")
        else:
            raise IOError("Truncated message")

    print(data)
    packed_msg_size = data[:payload_size]
    data = struct.unpack('Ibh',packed_msg_size)
    print(data)

    if not OfferPacket.validatePacket(data):
        print("Recieved a message which is not an offer message. Please try sending again")
    
    print(f"Received offer from {addr}, attempting to connect...")

# clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# clientSocket.listen(server_port)
# clientSocket.connect((serverName, server_port))
# clientSocket.send(sentence)
# modifiedSentence = clientSocket.recv(1024)
# print('from Server:',modifiedSentence)
# clientSocket.close()

