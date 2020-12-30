import scapy.all as scapy

LOCAL_IP = scapy.get_if_addr(scapy.conf.ifcae)
SERVER_PORT = 2042
