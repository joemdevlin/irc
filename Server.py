# Python program to implement server side of chat room.  
import socket 
import sys  
import _thread
from datetime import datetime
import argparse


parser = argparse.ArgumentParser(description='IRC like server')
parser.add_argument('--port', type=int, nargs='?', default=4137,
                    help='port for the server to listen to.')
parser.add_argument('--address', nargs='?',  default='localhost',
                    help='the address for the server to run on.')

cmdArgs = parser.parse_args()
print(cmdArgs.port)
print(cmdArgs.address)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  
server.bind((cmdArgs.address, cmdArgs.port))  
server.listen(10)

clients = [] 
rooms = ['General']

class Client:
    def __init__(self, conn, addr):
        self.conn = conn
        self.addr = addr
        self.rooms = []
        self.userName = None
    
    def addRoom(self, room):
        if not room in self.rooms:
            self.rooms.append(room)
    
    def removeRoom(self, room):
        self.rooms.remove(room)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False
  
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
    # Check high level structure of the message 
    parts = message.split(" ", 2)
    if len(parts) != 3:
        if len(parts) == 2 and "ROOM" in message:
            pass
        else:
            print("Bad fromat based on split. Size: " + str(len(parts)))
            return

    # Adding a new user.
    if parts[0] == "REGISTER":
        if parts[1] == "UNIQUE":
            if all([c.userName != parts[2] for c in clients]):
                client.userName = parts[2]
            else:
                print("Duplicate name: " + parts[2])#handel error message
    
    # Getting all the current chat rooms.
    elif parts[0] == "LIST":
        if parts[1] == "ROOMS":
            response = "ROOMS ALL " + " ".join(rooms)
            sendMessage(response.encode('utf-8'), client)

    # Join a new chat room
    elif parts[0] == "JOIN_ROOM":
        if parts[1] in rooms:
            client.addRoom(parts[1])
        else:
            print("Unknown chat room name")# Error

    # Create a new chat room.
    elif parts[0] == "CREATE_ROOM":
        if not parts[1] in rooms and not ',' in parts[1]:
            rooms.append(parts[1])
        else:
            print("Room already created")# Error

    # Exit a room
    elif parts[0] == "LEAVE_ROOM":
        if parts[1] in rooms:
            client.removeRoom(parts[1])
        else:
            print("Room already created")# Error

    # Send a message to others
    elif parts[0] == "SEND_MSG":
        if client.userName == None:
            print("User not registered.")
        elif parts[1] in rooms and parts[1] in client.rooms:
            message = client.userName + " " + datetime.now().strftime('%H:%M:%S') + " " + parts[2]
            temp = "REC_MSG " + parts[1] + " " + message
            broadcast(temp.encode('utf-8'), parts[1])
        else:
            print("Unknown chat room name or not a member of this room")# Error
    
    # Disconnect
    elif parts[0] == "DISCONNECT":
        if parts[1] == "ALL":
            disconnect(client)
        else:
            print("Unknown chat room name or not a member of this room")# Error

    # Hang on there bud. This is not supported
    else:
        print("Unknown operation")# handel error

def sendMessage(message, client):
        try:  
            client.conn.send(message)  
        except socket.error:  
            client.conn.close()   
            disconnect(client)  
 
def broadcast(message, room):  
    for client in clients: 
        if room in client.rooms: 
            sendMessage(message, client)

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