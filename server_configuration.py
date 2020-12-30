import scapy.all as scapy

LOCAL_IP = scapy.get_if_addr("eth0")
SERVER_PORT = 2042
