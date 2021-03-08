import socket  
import sys  
import _thread
import time
import select
from prompt_toolkit import prompt
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import WordCompleter
import argparse

# Represents a chat history in a specific room
class ChatRoom:
    def __init__(self, name):
        self.name = name   # Name of the room
        self.messages = [] # All messages recieved
        self.read = 0      # How many of the messages have been read so far
        self.memmbers = []
    
    def addMessage(self, msg):
        self.messages.append(msg)
    
    def setMembers(self, mem):
        self.memmbers = mem

    def readUnreadMessages(self):
        unread =  self.messages[self.read:]
        self.read = len(self.messages)
        return unread

# Allow for IP and port customization 
parser = argparse.ArgumentParser(description='IRC like server')
parser.add_argument('--port', type=int, nargs='?', default=4137,
                    help='port for the server to listen to.')
parser.add_argument('--address', nargs='?',  default='localhost',
                    help='the address for the server to run on.')
cmdArgs = parser.parse_args()
print(cmdArgs.port)
print(cmdArgs.address)
cmdArgs = parser.parse_args()

chatHistory={}
errorLog = ChatRoom("Server Errors")
continueFlag = True
# Repl commandline interface thread
def userInterface():
    global continueFlag
    completer = WordCompleter(['register', 'get_rooms',
         'show_rooms', 'show_errors', 'add', 'join', 'leave', 'disconnect',
          'read', 'send', 'get_members', 'show_members', 'exit'], ignore_case=True)
    
    while continueFlag:
        userInput = prompt('IRC>', history=FileHistory('history.txt'),
            auto_suggest=AutoSuggestFromHistory(), completer=completer)

        args = userInput.split(" ", 2)
        toSend = [] # Strings to be send to the server.

        # Server specific requests
        if args[0] == "register" and len(args) == 2:
            toSend.append("REGISTER UNIQUE " + args[1])
        elif args[0] == "get_rooms":
            toSend.append("LIST ROOMS")
        elif args[0] == "join" and len(args) == 2:
            rooms = args[1].split(',')
            for room in rooms:
                toSend.append("JOIN_ROOM " + room)
        elif args[0] == "add" and len(args) == 2:
            rooms = args[1].split(',')
            for room in rooms:
                toSend.append("CREATE_ROOM " + room)
        elif args[0] == "leave" and len(args) == 2:
            rooms = args[1].split(',')
            for room in rooms:
                toSend.append("LEAVE_ROOM " + room)
        elif args[0] == "send" and len(args) == 3:
            for room in args[1].split(','):
                toSend.append("SEND_MSG " + room + " " + args[2])
        elif args[0] == "disconnect":
            toSend.append("DISCONNECT ALL")
            continueFlag = False
        elif args[0] == 'get_members' and len(args) == 2:
            toSend.append("LIST_ROOM_MEMBERS " + args[1])
  
        # Opreations that do not require the server
        elif args[0] == "show_rooms":
            for room in chatHistory.keys():
                print(room)
            continue

        # Display memembers of a certain chat room.
        elif args[0] == "show_members":
            room = args[1]
            if room in chatHistory.keys():
                for msg in chatHistory[room].memmbers:
                    print(msg)
            else:
                print("Error: Room is not valid")
            continue

        # Read messages from specfici rooms
        elif args[0] == "read":
            room = args[1]
            if room in chatHistory.keys():
                if len(args) != 3 or (not args[2] in ["ALL","UNREAD"]):
                    print("Error: expected third paramters ALL|UNREAD")
                    continue
                msgs = []
                if args[2] == "ALL":
                    msgs = chatHistory[room].messages
                else:
                    msgs = chatHistory[room].readUnreadMessages()
                for msg in msgs:
                    print(msg)
            else:
                print("Error: Room is not valid")
            continue
        
        # Displays errors recieved by the server
        elif args[0] == "show_errors":
            for msg in errorLog.readUnreadMessages():
                print(msg)
            continue

        elif args[0] == 'exit':
            sys.exit()

        if toSend == []:
            print("ERROR with commmand: " + userInput)
        for msg in toSend:
            formatted = msg + '\0'
            server.sendall(formatted.encode('utf-8'))

# Thrad for handling REPL
_thread.start_new_thread(userInterface,()) 

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  
server.connect((cmdArgs.address, cmdArgs.port))  
server.settimeout(.1)

# Main thread listens for feedback from the server.
while continueFlag: 
    data = None  
    try:
        data = server.recv(2048)
    except socket.timeout:
        continue
    except Exception as e:
        print("Server connection error.")
        sys.exit()

    if data:   
        msg = data.decode('utf-8').split(" ", 2)
        if msg[0] == "REC_MSG":
            room = msg[1]
            if not room in chatHistory.keys():
                chatHistory[room] = ChatRoom(room)
            chatHistory[room].addMessage(msg[2])
        
        elif msg[0] == "ROOMS":
            allRooms = msg[2].split(" ")
            for room in allRooms:
                if not room in chatHistory.keys():
                    chatHistory[room] = ChatRoom(room)

        elif msg[0] == "ROOM_MEMBERS":
            room = msg[1]
            allRooms = msg[2].split(" ")
            if not room in chatHistory.keys():
                chatHistory[room] = ChatRoom(room)
            chatHistory[room].setMembers(allRooms)

        elif msg[0].startswith("ERR_"):
            errorLog.addMessage(" ".join(msg))
    else:
        break
server.close()  