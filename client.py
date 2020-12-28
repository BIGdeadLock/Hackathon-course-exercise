from socket import *
serverName='serverName'
server_port = 13117
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.listen(server_port)
clientSocket.connect((serverName, server_port))
sentence = print('Client started, listening for offer requests...')
clientSocket.send(sentence)
modifiedSentence = clientSocket.recv(1024)
print('from Server:',modifiedSentence)
clientSocket.close()