import base64
import cv2
import numpy as np
import math
import socket

import time

SERVER_IP = '127.0.0.1'


def decodePacket(packet):
    packet_seq = int.from_bytes(packet[0:2], "little", signed=False)
    tot = int.from_bytes(packet[2:4], "little", signed=False)
    curr = int.from_bytes(packet[4:6], "little", signed=False)
    data = packet[6:]
    # print("Header| " + " Seq: " + str(packet_seq) + " | Total: " +
    #     str(tot) + " | Curr: " + str(curr) + "|")

    return packet_seq, tot, curr, data


def decodeAndShowImage(img):
    npimg = np.fromstring(base64.b64decode(img), dtype=np.uint8)
    source = cv2.imdecode(npimg, 1)
    cv2.imshow("Stream", source)
    cv2.waitKey(1)


# MAIN

serversocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
serversocket.bind((SERVER_IP, 7777))

print("SERVER STARTED")

# Contain chunks of frame in order (number of cell = total number of chunks in header)
packets = []
seq = -1  # Sequence number of frames
counter = 0  # Count how many chunks of the current frame already received

rcv_frame_delta = 0

last_reset = time.time()

while True:
    d, a = serversocket.recvfrom(4096)  # Check if a chunks arrived

    delta = time.time() - last_reset
    if delta > 0.2:
        last_reset = time.time()
        print("  FPS: " + str(int(rcv_frame_delta / delta)) + "              ", end='\r')
        
        rcv_frame_delta = 0

    if d:
        # sequence number, number of chunks of the frame, current chunks, chunks data
        packet_seq, tot, curr, data = decodePacket(d)

        # if a most recent frame arrived, discard the oldest one
        if packet_seq != seq:
            packets = [None] * tot
            seq = packet_seq
            counter = 0

        # Put chunk in order
        packets[curr] = data
        counter += 1

        # if number of chunks received = total chunks number of the frame assemble and show the image
        if counter == tot:
            img = b''
            for i in packets:
                img = img + i

            rcv_frame_delta += 1
            decodeAndShowImage(img)
