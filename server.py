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

    b64 = base64.b64decode(img)

    if b64[0:2] == b'\xff\xd8' and b64[-2:] == b'\xff\xd9': #JPG checksum
        npimg = np.fromstring(b64, dtype=np.uint8)
        source = cv2.imdecode(npimg, 1)
        cv2.imshow("Stream", source)
        cv2.waitKey(1)
    else:
        print("JPG ERROR")


# MAIN
serversocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
serversocket.bind((SERVER_IP, 7777))

print("SERVER STARTED")

# Contain chunks of frame in order (number of cell = total number of chunks in header)
packets = [None] * 100
seq = -1  # Sequence number of frames
counter = 0  # Count how many chunks of the current frame already received

rcv_frame_delta = 0

last_reset = time.time()

while True:
    d, a = serversocket.recvfrom(4096)  # Check if a chunks arrived

    delta = time.time() - last_reset
    if delta > 0.2:
        last_reset = time.time()
        print("  FPS: " + str(int(rcv_frame_delta / delta)) +
              "              ", end='\r')

        rcv_frame_delta = 0

    if d:
        # sequence number, number of chunks of the frame, current chunks, chunks data
        packet_seq, tot, curr, data = decodePacket(d)

        # if a most recent frame arrived, discard the oldest one (!= since if crash and restart sequence are zeroed)
        if packet_seq != seq:
            seq = packet_seq
            counter = 0

        # Put chunk in order
        if counter == curr: # out of synch only if new frame arrived (wait for a new one)
            packets[curr] = data
            counter += 1

        '''print()
        print("Packet sequnece:" + str(packet_seq))
        print("Saved sequnece:" + str(seq))

        print("Curr:" + str(curr))
        print("counter:" + str(counter))'''


        # If number of chunks received = total chunks number of the frame assemble and show the image
        if counter == tot:
            img = b''
            for i in range(0, tot):
                img = img + packets[i]

            rcv_frame_delta += 1
            decodeAndShowImage(img)
