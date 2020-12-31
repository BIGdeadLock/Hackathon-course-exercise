import scapy.all as scapy

LOCAL_IP = scapy.get_if_addr(scapy.conf.iface)
SERVER_PORT = 2042
SOCKET_TIMEOUT = 10
SOCKET_NONBLOCKING = 0
BUSY_WAITING_AVOIDANCE = 0.5