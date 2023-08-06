import socket

import sys 
sys.path.append("..")
try:
    from bagbag.Tools import Chan
    from bagbag.Thread import Thread 
except:
    from Tools import Chan
    from Thread import Thread

class TCPPeerAddress():
    def __init__(self, host:str, port:int):
        self.Host = host 
        self.Port = port 
    
    def __str__(self) -> str:
        return f"TCPPeerAddress(Host={self.Host}, Port={self.Port})"
    
    def __repr__(self) -> str:
        return self.__str__()
        
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

        Thread(self.acceptloop)
    
    def acceptloop(self):
        while True:
            ss, addr = self.s.accept()
            self.q.Put(StreamConnection(ss, addr[0], addr[1]))
    
    def Accept(self) -> Chan[StreamConnection]:
        return self.q
    
    def AcceptOne(self) -> StreamConnection:
        return self.q.Get()
    
    def Close(self):
        self.s.close()

def Connect(host:str, port:int) -> StreamConnection:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
    s.connect((host, port))  
    return StreamConnection(s, host, port)

if __name__ == "__main__":
    def server():
        print("listen on: ", "127.0.0.1", 22222)
        l = Listen("127.0.0.1", 22222)
        for s in l.Accept():
            print("Connect from:",s.PeerAddress())
            print("Receive:",s.Recv(512))
            print("Close on server side")
            s.Close()
        
    Thread(server)

    import time 
    time.sleep(2)

    def client():
        print("connect to", "127.0.0.1", 22222)
        s = Connect("127.0.0.1", 22222)
        s.Send(str(int(time.time())))
        time.sleep(1)
        print("Close on client side")
        s.Close()

    for _ in range(10):
        client()
        time.sleep(1)