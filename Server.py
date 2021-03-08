# Python program to implement server side of chat room.  
import socket 
import sys  
import _thread
from datetime import datetime
from Common import getArgs


# Allow for IP and port customization 
port, address = getArgs()
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  
server.bind((address, port))
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

    def __str__(self):
        return str(self.userName) + "\n\t" + ",".join(self.rooms)
  
# Spawning a serperate thread per conenction to relay the message
def clientthread(client):
    buffer = ""  
    while True:  
        try:  
            data = client.conn.recv(2048).decode('utf-8')
            if data:
                buffer = buffer + data
                messages = buffer.split('\0')
                for m in messages[:-1]:
                    if data: 
                        parseMessage(m, client)
                buffer = messages[-1]
            else:  
                disconnect(client)  
        except Exception as e:
            print(e)
            disconnect(client) 

def parseMessage(message, client):
    # Check high level structure of the message 
    print(client)
    print(message)
    parts = message.split(" ", 2)
    if len(parts) != 3:
        if len(parts) == 2 and ("ROOM" in message or parts[0] == "DISCONNECT") :
            pass
        else:
            print("Bad fromat based on split. Size: " + str(len(parts)))
            msg = "ERR_UNKNOWN FORMAT " + message
            sendMessage(msg, client)
            return 

    # Spec does not define the expcected behavior for sending a different first message.
    # This server will choose to disconnect.
    if client.userName == None and parts[0] != "REGISTER":
        disconnect(client)

    # Adding a new user.
    elif parts[0] == "REGISTER":
        if parts[1] == "UNIQUE":
            if all([c.userName != parts[2] for c in clients]):
                client.userName = parts[2]
            else:
                print("Duplicate name: " + parts[2])
                msg = "ERR_REGISTER USER_EXISTS " + message
                sendMessage(msg, client)
    
    # Getting all the current chat rooms.
    elif parts[0] == "LIST":
        if parts[1] == "ROOMS":
            response = "ROOMS ALL " + " ".join(rooms)
            sendMessage(response, client)

    # Getting the members of a room
    elif parts[0] == "LIST_ROOM_MEMBERS":
        if parts[1] in rooms:
            members = []
            for client in clients:
                if parts[1] in client.rooms:
                    members.append(client.userName)
            response = "ROOM_MEMBERS " + parts[1] + " " + " ".join(members)
            sendMessage(response, client)
        else:
            print("Unknown chat room name")
            msg = "ERR_ROOM UNKNOWN " + message
            sendMessage(msg, client)

    # Join a new chat room
    elif parts[0] == "JOIN_ROOM":
        if parts[1] in rooms:
            client.addRoom(parts[1])
        else:
            print("Unknown chat room name")
            msg = "ERR_ROOM UNKNOWN " + message
            sendMessage(msg, client)
            

    # Create a new chat room.
    elif parts[0] == "CREATE_ROOM":
        if not parts[1] in rooms and not ',' in parts[1]:
            rooms.append(parts[1])
        else:
            print("Room already created or invalid syntax")
            msg = "ERR_ROOM EXISTS " + message
            sendMessage(msg, client)

    # Exit a room
    elif parts[0] == "LEAVE_ROOM":
        if parts[1] in rooms:
            client.removeRoom(parts[1])
        else:
            print("Room already created")
            msg = "ERR_ROOM UNKNOWN " + message
            sendMessage(msg, client)

    # Send a message to others
    elif parts[0] == "SEND_MSG":
        if client.userName == None:
            print("User not registered.")
            msg = "ERR_UNKNOWN_USER None" + message
            sendMessage(msg, client)
        elif parts[1] in rooms and parts[1] in client.rooms:
            message = client.userName + " " + datetime.now().strftime('%H:%M:%S') + " " + parts[2]
            temp = "REC_MSG " + parts[1] + " " + message
            broadcast(temp, parts[1])
        else:
            print("Unknown chat room name or not a member of this room")
            msg = "ERR_ROOM NOT_REGISTED " + message
            sendMessage(msg, client)

    # User would like to disconnect from the server
    elif parts[0] == "DISCONNECT":
        if parts[1] == "ALL":
            disconnect(client)
        else:
            print("Unknown chat room name or not a member of this room")
            msg = "ERR_UNKNOWN ARG " + message
            sendMessage(msg, client)

    # Hang on there bud. This is not supported
    else:
        print("Unknown operation")
        msg = "ERR_UNKNOWN OP " + message
        sendMessage(msg, client)

# Send a messsage to an individual client
def sendMessage(message, client):
    try:  
        client.conn.send((message + '\0').encode('utf-8'))  
    except socket.error:
        disconnect(client)  
 
# Send a message to a room
def broadcast(message, room):  
    for client in clients: 
        if room in client.rooms: 
            sendMessage(message, client)

# Terminate communication with a client
def disconnect(c):  
    if c in clients:
        try:  
           c.conn.close() 
        except socket.error:  
            pass
        clients.remove(c)
    sys.exit()

# Parent thread listens for new connections
if __name__ == '__main__':  
    try:
        while True:  
            conn, addr = server.accept()  
            clients.append(Client(conn, addr))  
            print (addr[0] + " connected") 

            # Child threads handel each client connection.
            _thread.start_new_thread(clientthread, (clients[-1],)) 

    except KeyboardInterrupt:
        pass
    server.close()  