import base64
import cv2
import math
import socket

SERVER_IP = '127.0.0.1'


def getVideoFrame():
    grabbed, frame = camera.read()  # grab the current frame
    frame = cv2.resize(frame, (640, 480))  # resize the frame
    encoded, buffer = cv2.imencode('.jpg', frame)
    jpg_as_text = base64.b64encode(buffer)
    return jpg_as_text  # output byte array


def generatePacket(data, seq_number):
    packet_dimension = 4096 - 8  # Byte dimension of packet
    # number of packet to be generated to contain all data
    packet_number = math.ceil(len(data)/packet_dimension)

    packets = []
    for i in range(0, packet_number):
        # Genrate packet header
        # Structure
        # |Sequence Number(2)|Packet Number(2)|Current Packet(2)|Data(packet_dimension - 8)|
        header = seq_number.to_bytes(
            2, "little", signed=False) + packet_number.to_bytes(
            2, "little", signed=False) + i.to_bytes(2, "little", signed=False)

        # Split data into packets
        start = i * packet_dimension
        end = start + packet_dimension
        packet = header + data[start:end]
        packets.append(packet)

        print("Header| " + " Seq: " + str(seq_number) + " | Total: " +
              str(packet_number) + " | Curr: " + str(i) + "|", end ='\r')

    return packets


# MAIN
# Init
camera = cv2.VideoCapture(0)  # init the camera
clientsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
seq_number = 0
print("CLIENT STARTED")

# Loop
while True:
    img = getVideoFrame()
    data = generatePacket(img, seq_number)

    for i in data:
        clientsocket.sendto(i, (SERVER_IP, 7777))

    seq_number += 1
