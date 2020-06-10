# Python3
# Usage found on lines 16 & 18

import os
import sys
from signal import SIGINT, SIGTERM, signal
from socket import AF_INET, SOCK_DGRAM, SOCK_STREAM, socket
from threading import Thread
from time import sleep

LOCAL_HOST = '127.0.0.1'
PORT_OFFSET = 11700

if len(sys.argv) < 4 or len(sys.argv) > 6:
    print("Usage: ")
    print("python3 main.py init [peer_id] [first_succ_id] [second_succ_id] [--optional interval]")
    print("OR")
    print("python3 main.py join [peer_id] [known_peer] [--optional interval]")
    sys.exit(1)

class Peer:
    '''Peer class'''
    def __init__(self, entry, peerID, first_succ=-1, second_succ=-1, interval=10):
        self.id = int(peerID)
        self.port = int(peerID) + PORT_OFFSET
        self.first_succ = int(first_succ)
        self.first_succ_port = int(first_succ) + PORT_OFFSET
        self.first_succ_state = True
        self.files = []
        if entry == 'init':
            self.second_succ = int(second_succ)
            self.second_succ_port = int(second_succ) + PORT_OFFSET
            self.second_succ_state = True
            self.interval = int(interval)
        else:
            self.interval = int(second_succ)

    def updateSucc(self, first_succ, second_succ):
        self.first_succ = int(first_succ)
        self.first_succ_port = PORT_OFFSET + int(first_succ)
        self.second_succ = int(second_succ)
        self.second_succ_port = PORT_OFFSET + int(second_succ)

    def updatePred(self, preds):
        first_pred = max(preds)
        second_pred = min(preds)
        self.first_pred = int(first_pred)
        self.first_pred_port = PORT_OFFSET + int(first_pred)
        self.second_pred = int(second_pred)
        self.second_pred_port = PORT_OFFSET + int(second_pred)

    def serverSetup(self):
        pingServer = self.UDPServer(self, "Server")
        pingServer.start()
        tcpServer = self.TCPServer(self, "TCPServer")
        tcpServer.start()
        sleep(5)

    def activatePeer(self):
        pingClient = self.PingClient(self, "Client")
        pingClient.start()
        inputInfo = self.InputInfo(self, "User-Input")
        inputInfo.start()

    def joinPeer(self):
        if self.id == self.first_succ:
            print("/decline 'This id already exists'")
        message = f"/join {self.first_succ} {self.id}"
        self.sendTCPmessage(message, (LOCAL_HOST, self.first_succ_port))
    
    def fileStorer(self, filenum):
        if self.id == filenum%256:
            self.files.append(filenum)
            print(f"Store {filenum} request accepted")
        else:
            message = f"/store {filenum} {self.first_succ} {self.id}"
            self.sendTCPmessage(message, (LOCAL_HOST, self.first_succ_port))
            print(f"Store {filenum} request forwarded to my successor")

    def fileFinder(self, filenum, src):
        if self.id >= filenum%256:
            if filenum in self.files:
                print(f"File {filenum} is stored here")
                print(f"Sending file {filenum} to Peer {src}")
                message = f"/deliver {filenum} {src} {self.id}"
                self.sendTCPmessage(message, (LOCAL_HOST, src + PORT_OFFSET))
                print(f"The file has been sent")
            else:
                print(f"Request for File {filenum} has been received, but the file is not stored here")
                message = f"/request {filenum} {self.first_succ} {src}"
                self.sendTCPmessage(message, (LOCAL_HOST, self.first_succ_port))
        else:
            message = f"/request {filenum} {self.first_succ} {src}"
            self.sendTCPmessage(message, (LOCAL_HOST, self.first_succ_port))

    @classmethod
    def sendUDPmessage(cls, message, address):
        sock = socket(AF_INET, SOCK_DGRAM)
        sock.sendto(message.encode('utf-8'), address)

    @classmethod
    def sendTCPmessage(cls, message, address):
        sock = socket(AF_INET, SOCK_STREAM)
        sock.connect(address)
        sock.send(message.encode('utf-8'))

    class UDPServer(Thread):
        '''
        UDP Server
        '''
        def __init__(self, peer, name):
            Thread.__init__(self)
            self.name = name
            self.peer = peer

        def run(self):
            sock = socket(AF_INET, SOCK_DGRAM)
            sock.bind((LOCAL_HOST, self.peer.port))
            preds = []
            while True:
                message = sock.recvfrom(2048)
                parsed = message[0].decode('utf-8')
                # print(parsed)
                info = parsed.split(" ")
                dest = int(info[1])
                src = int(info[2])
                if dest != self.peer.id:
                    print(f"Stray message received from {src}:")
                    print(parsed)
                if info[0] == '/ping':
                    print(f"Ping request message received from {src}")
                    src_port = src + PORT_OFFSET
                    response = f"/response {src} {self.peer.id}"
                    Peer.sendUDPmessage(response, (LOCAL_HOST, src_port))
                    if len(preds) < 2 and src not in preds:
                        preds.append(src)
                    elif len(preds) == 2:
                        self.peer.updatePred(preds)
                    elif src not in preds:
                        preds = []
                        preds.append(src)
                if info[0] == '/response':
                    print(f"Ping response received from Peer {src}")

    class TCPServer(Thread):
        '''
        TCP Server
        '''
        def __init__(self, peer, name):
            Thread.__init__(self)
            self.name = name
            self.peer = peer
        
        def run(self):
            sock = socket(AF_INET, SOCK_STREAM)
            sock.bind((LOCAL_HOST, self.peer.port))
            sock.listen(10)
            while True:
                conn, addr = sock.accept()
                message = conn.recv(2048)
                parsed = message.decode('utf-8')
                info = parsed.split(" ")
                src = int(info[-1])
                src_port = src + PORT_OFFSET
                dest = int(info[-2])
                if dest == self.peer.id:
                    if info[0] == '/join':
                        if src == self.peer.first_succ \
                            or src == self.peer.second_succ:
                            # This id already exists in the network
                            response = f"/decline 'This id already exists' {src} {self.peer.id}"
                            Peer.sendTCPmessage(response, (LOCAL_HOST, src))
                        elif (src > self.peer.id and src < self.peer.first_succ) or \
                            (self.peer.id > self.peer.first_succ and src > self.peer.id):
                            # An appropriate place has been found in the network
                            response = f"/accept {self.peer.first_succ} {self.peer.second_succ} {src} {self.peer.id}"
                            print(f"Peer {src} Join request received")
                            self.peer.updateSucc(src, self.peer.first_succ)
                            pred = f"/successor {self.peer.id} {self.peer.first_succ} {self.peer.first_pred} {self.peer.id}"
                            print(f"My new first successor is Peer {self.peer.first_succ}")
                            print(f"My new second successor is {self.peer.second_succ}")
                            Peer.sendTCPmessage(response, (LOCAL_HOST, src_port))
                            Peer.sendTCPmessage(pred, (LOCAL_HOST, self.peer.first_pred_port))
                        else:
                            # Request needs to be forwarded
                            forward = f"/join {self.peer.first_succ} {src}"
                            self.peer.sendTCPmessage(forward, (LOCAL_HOST, self.peer.first_succ_port))
                            print(f"Peer {src} Join request forwarded to my successor")
                    elif info[0] == '/decline':
                        print(parsed)
                        os._exit(0)
                    elif info[0] == '/accept':
                        print(f"Join request has been accepted")
                        self.peer.updateSucc(int(info[1]), int(info[2]))
                        print(f"My first successor is {self.peer.first_succ}")
                        print(f"My second successor is {self.peer.second_succ}")
                        self.peer.activatePeer()
                    elif info[0] == '/successor':
                        print(f"Successor Change request received")
                        self.peer.updateSucc(int(info[1]), int(info[2]))
                        print(f"My first successor is {self.peer.first_succ}")
                        print(f"My second successor is {self.peer.second_succ}")
                    elif info[0] == '/leave':
                        print(f"Peer {src} will depart from the network")
                        self.peer.updateSucc(int(info[1]), int(info[2]))
                        print(f"My first successor is {self.peer.first_succ}")
                        print(f"My second successor is {self.peer.second_succ}")
                    elif info[0] == '/store':
                        self.peer.fileStorer(int(info[1]))
                    elif info[0] == '/request':
                        self.peer.fileFinder(int(info[1]), src)
                    elif info[0] == '/deliver':
                        print(f"Peer {src} had File {info[1]}")
                        print(f"Receiving File {info[1]} from Peer {src}")
                        print(f"File {info[1]} received")
                conn.close()
            sock.close()
        
    class PingClient(Thread):
        def __init__(self, peer, name):
            Thread.__init__(self)
            self.name = name
            self.peer = peer

        def run(self):
            while True:
                ping1 = f"/ping {self.peer.first_succ} {self.peer.id}"
                ping2 = f"/ping {self.peer.second_succ} {self.peer.id}"
                Peer.sendUDPmessage(ping1, (LOCAL_HOST, self.peer.first_succ_port))
                Peer.sendUDPmessage(ping2, (LOCAL_HOST, self.peer.second_succ_port))
                print(f"Ping requests sent to Peers {self.peer.first_succ} and {self.peer.second_succ}")
                sleep(self.peer.interval)

    class InputInfo(Thread):
        def __init__(self, peer, name):
            Thread.__init__(self)
            self.name = name
            self.peer = peer

        def run(self):
            while True:
                user_input = input().lower()
                info = user_input.split(" ")
                if info[0] == 'quit':
                    second_pred = f"/leave {self.peer.first_pred} {self.peer.first_succ} {self.peer.second_pred} {self.peer.id}"
                    first_pred = f"/leave {self.peer.first_succ} {self.peer.second_succ} {self.peer.first_pred} {self.peer.id}"
                    Peer.sendTCPmessage(second_pred, (LOCAL_HOST, self.peer.second_pred_port))
                    Peer.sendTCPmessage(first_pred, (LOCAL_HOST, self.peer.first_pred_port))
                    print("Client has left"+'\n')
                    os._exit(0)
                elif info[0] == 'store':
                    self.peer.fileStorer(int(info[1]))
                elif info[0] == 'request':
                    filenum = int(info[1])
                    if filenum in self.peer.files:
                        print(f"File {filenum} is stored with you")
                    else:
                        self.peer.fileFinder(filenum, self.peer.id)

def exitProgram(signal, frame):
    print("\nProgram is terminated")
    os._exit(0)

if __name__ == "__main__":
    signal(SIGINT, exitProgram)
    signal(SIGTERM, exitProgram)
    peer = Peer(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
    peer.serverSetup()
    if sys.argv[1] == 'init':
        peer.activatePeer()
    elif sys.argv[1] == 'join':
        peer.joinPeer()
    else:
        print("Usage: ")
        print("python3 main.py init [peer_id] [first_succ_id] [second_succ_id] [--optional interval]")
        print("OR")
        print("python3 main.py join [peer_id] [known_peer] [--optional interval]")
        sys.exit(1)
