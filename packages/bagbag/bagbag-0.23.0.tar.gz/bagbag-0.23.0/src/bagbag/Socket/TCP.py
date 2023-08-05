import socket

import sys 
sys.path.append("..")
from Tools import Chan

class TCPPeerAddress():
    def __init__(self, host:str, port:int):
        self.Host = host 
        self.Port = port 
        
class StreamConnection():
    def __init__(self, ss:socket, host:str, port:int):
        self.ss = ss
        self.host = host
        self.port = port 
    
    def PeerAddress(self) -> TCPPeerAddress:
        return TCPPeerAddress(self.host, self.port)
    
    def Send(self, data:str):
        self.ss.sendall(data.encode('utf-8'))

    def SendBytes(self, data:bytes):
        self.ss.sendall(data) 

    def Recv(self, length:int) -> str:
        return self.ss.recv(length).decode('utf-8')

    def RecvBytes(self, length:int) -> bytes:
        return self.ss.recv(length)
    
    def Close(self):
        self.ss.close()

class Listen():
    def __init__(self, host:str, port:int, waitQueue:int=5):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.bind((host, port))
        self.s.listen(waitQueue)

        self.q:Chan[StreamConnection] = Chan(10)
    
    def Accept(self) -> Chan[StreamConnection]:
        while True:
            ss, addr = self.s.accept()
            self.q.Put(StreamConnection(ss, addr[0], addr[1]))
    
    def AcceptOne(self) -> StreamConnection:
        ss, addr = self.s.accept()
        return StreamConnection(ss, addr[0], addr[1])
    
    def Close(self):
        self.s.close()

def Connect(host:str, port:int) -> StreamConnection:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
    s.connect((host, port))  
    return StreamConnection(s, host, port)

