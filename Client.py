import socket  
import sys  
import _thread
import time
import select
from prompt_toolkit import prompt
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import WordCompleter
from Common import getArgs

# Represents a chat history in a specific room
class ChatRoom:
    def __init__(self, name):
        self.name = name   # Name of the room
        self.messages = [] # All messages recieved
        self.read = 0      # How many of the messages have been read so far
        self.members = []  # Name of the users that are connected to the channel
    
    def addMessage(self, msg):
        self.messages.append(msg)
    
    def setMembers(self, mem):
        self.members = filter(lambda x: x.strip() != "", mem)

    def readUnreadMessages(self):
        unread =  self.messages[self.read:]
        self.read = len(self.messages)
        return unread

# These are updated by the parent listening thread, and then read by the child tread.
# They contain updates from the server side.
chatHistory={}
errorLog = ChatRoom("Server Errors")

# Global flag to decide if the user has tried to terminate the connection. It is set
# in the child process, and then read in the parent process.
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

        # Assign a user name to the connection
        if args[0] == "register" and len(args) == 2:
            toSend.append("REGISTER UNIQUE " + args[1])

        # Ask the server for a list of chat rooms
        elif args[0] == "get_rooms":
            toSend.append("LIST ROOMS")

        # Join a room
        elif args[0] == "join" and len(args) == 2:
            rooms = args[1].split(',')
            for room in rooms:
                toSend.append("JOIN_ROOM " + room)
        
        # Create a new room
        elif args[0] == "add" and len(args) == 2:
            rooms = args[1].split(',')
            for room in rooms:
                toSend.append("CREATE_ROOM " + room)
        
        # Leave a room
        elif args[0] == "leave" and len(args) == 2:
            rooms = args[1].split(',')
            for room in rooms:
                toSend.append("LEAVE_ROOM " + room)

        # Send a message to a room(s)
        elif args[0] == "send" and len(args) == 3:
            for room in args[1].split(','):
                toSend.append("SEND_MSG " + room + " " + args[2])

        # Terminate connection with server
        elif args[0] == "disconnect":
            toSend.append("DISCONNECT ALL")
            continueFlag = False
        
        # Ask the server for the list of members in a room
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
                for msg in chatHistory[room].members:
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

        # User is done
        elif args[0] == 'exit':
            continueFlag = False
            sys.exit()

        # Client side only commands will continue, so they will not reach here.
        if toSend == []:
            print("ERROR with commmand: " + userInput)

        # Each command creates some number of requests to be sent to the server.
        for msg in toSend:
            formatted = msg + '\0'
            server.sendall(formatted.encode('utf-8'))

def processMessage(message):
    msg = message.split(" ", 2)

    # Message recieved from a user
    if msg[0] == "REC_MSG":
        room = msg[1]
        if not room in chatHistory.keys():
            chatHistory[room] = ChatRoom(room)
        chatHistory[room].addMessage(msg[2])
    
    # List of all rooms
    elif msg[0] == "ROOMS":
        allRooms = msg[2].split(" ")
        for room in allRooms:
            if not room in chatHistory.keys():
                chatHistory[room] = ChatRoom(room)

    # List of all members in a room
    elif msg[0] == "ROOM_MEMBERS":
        room = msg[1]
        allRooms = msg[2].split(" ")
        if not room in chatHistory.keys():
            chatHistory[room] = ChatRoom(room)
        chatHistory[room].setMembers(allRooms)

    # Error generated from a pervious request
    elif msg[0].startswith("ERR_"):
        errorLog.addMessage(" ".join(msg))

# Thrad for handling REPL
_thread.start_new_thread(userInterface,()) 

# Connecting to the server
port, address = getArgs()
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  
server.connect((address, port))
server.settimeout(.1)

# Main thread listens for feedback from the server.
while continueFlag: 
    # Check for data
    buffer = ""  
    while True:  
        try:  
            data = server.recv(2048).decode('utf-8')
            if data:
                buffer = buffer + data
                messages = buffer.split('\0')
                for m in messages[:-1]:
                    if data: 
                        processMessage(m)
                buffer = messages[-1]
            else:
                print("Disconnected from server.")
                continueFlag = False
                break
        except socket.timeout:
            break
        except socket.error as e:
            print("Server connection error.")
            sys.exit()
        except Exception as e:
            print("Unexpected error.")
            sys.exit()
    data = None  
server.close()  