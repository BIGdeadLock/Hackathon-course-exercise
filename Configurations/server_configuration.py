import scapy.all as scapy

LOCAL_IP = scapy.get_if_addr(scapy.conf.iface)
SERVER_PORT = 2042
SOCKET_TIMEOUT = 10
SOCKET_NONBLOCKING = 0
BUSY_WAITING_AVOIDANCE = 1
GROUP1_NUMBER = 1
GROUP2_NUMBER = 2
