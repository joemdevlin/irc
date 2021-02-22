import socket  
import sys  
import _thread
import time
from prompt_toolkit import prompt
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import WordCompleter
import argparse

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

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  
server.connect((cmdArgs.address, cmdArgs.port))  

chatHistory={}

# Represents a chat history in a specific room
class ChatRoom:
    def __init__(self, name):
        self.name = name   # Name of the room
        self.messages = [] # All messages recieved
        self.read = 0      # How many of the messages have been read so far
    
    def addMessage(self, msg):
        self.messages.append(msg)
    
    def readUnreadMessages(self):
        unread =  self.messages[self.read:]
        self.read = len(self.messages)
        return unread

def userInterface():
    completer = WordCompleter(['register', 'refresh_rooms',
         'show_rooms', 'add', 'join', 'leave', 'disconnect',
          'read', 'send'], ignore_case=True)
    
    while 1:
        userInput = prompt('IRC>', history=FileHistory('history.txt'),
            auto_suggest=AutoSuggestFromHistory(), completer=completer)

        args = userInput.split(" ", 2)
        toSend = [] # Strings to be send to the server.

        # Server specific requests
        if args[0] == "register":
            toSend.append("REGISTER UNIQUE " + args[1])
        elif args[0] == "refresh_rooms":
            toSend.append("LIST ROOMS")
        elif args[0] == "join":
            toSend.append("JOIN_ROOM " + args[1])
        elif args[0] == "add":
            toSend.append("CREATE_ROOM " + args[1])
        elif args[0] == "leave":
            toSend.append("LEAVE_ROOM " + args[1])
        elif args[0] == "send":
            for room in args[1].split(','):
                toSend.append("SEND_MSG " + room + " " + args[2])
        elif args[0] == "disconnect":
            #TODO
            pass
        
        # Opreations that do not require the server
        elif args[0] == "show_rooms":
            for room in chatHistory.keys():
                print(room)
            continue
        elif args[0] == "read":
            room = args[1]
            if room in chatHistory.keys():
                for msg in chatHistory[room].readUnreadMessages():
                    print(msg)
            else:
                print("Error: Room is not valid")
            continue

        if toSend == []:
            print("ERROR with commmand: " + userInput)
        for msg in toSend:
            server.send(msg.encode('utf-8'))

# Thrad for handling REPL
_thread.start_new_thread(userInterface,()) 

# Main thread listens for feedback from the server.
while True:   
    data = server.recv(2048)
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

server.close()  