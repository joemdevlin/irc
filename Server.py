# Python program to implement server side of chat room.  
import socket 
import sys  
import _thread
class Client:
    def __init__(self, conn, addr):
        self.conn = conn
        self.addr = addr
        self.rooms = []
        self.userName = None
    
    def addRoom(self, room):
        self.rooms.append(room)
    
    def removeRoom(self, room):
        self.rooms.remove(room)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  
    
ip = 'localhost'  
port = 4137
server.bind((ip, port))  
server.listen(10)

clients = [] 
rooms = ['General']
  
# Spawning a serperate thread per conenction to relay the message
def clientthread(client):  
    while True:  
        try:  
            data = conn.recv(2048) 
            if data: 
                parseMessage(data.decode('utf-8'), client)
            else:  
                disconnect(client)  

        except socket.error as e: 
            print(e) 
            continue

def parseMessage(message, client): 
    parts = message.split(" ", 3)
    if len(parts) != 3:
        return
    op, parameter, message = parts
    if op == "REGISTER":
        if parameter == "UNIQUE":
            client.userName = message
    else:
        temp = str(client.userName) + ": " + message
        broadcast(temp.encode('utf-8'))

def broadcast(message):  
    for client in clients:  
        try:  
            client.conn.send(message)  
        except socket.error:  
            client.conn.close()   
            disconnect(client)   

def disconnect(c):  
    if c in clients:  
        c.remove(c)  

if __name__ == '__main__':  
    try:
        while True:  
            conn, addr = server.accept()  
            clients.append(Client(conn, addr))  
            print (addr[0] + " connected") 
 
            _thread.start_new_thread(clientthread, (clients[-1],)) 
                    
    except KeyboardInterrupt:
        pass
    server.close()  