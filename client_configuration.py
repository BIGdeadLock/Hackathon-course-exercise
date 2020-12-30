from offer import OfferPacket
import scapy.all as scapy

PAYLOAD_SIZE = OfferPacket.payload_size
LOCAL_IP = scapy.get_if_addr("eth0")
SERVER_DEST_PORT = 2042
TEAM_NAME = "ROCKET_TEAM\n"
