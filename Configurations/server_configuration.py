import scapy.all as scapy

LOCAL_IP = scapy.get_if_addr(scapy.conf.iface)
SERVER_PORT = 2042
