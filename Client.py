import socket  
import sys  
import _thread
import time
from prompt_toolkit import prompt
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import WordCompleter

class ChatRoom:
    def __init__(self, name):
        self.name = name
        self.messages = []
        self.read = 0
    
    def addMessage(self, msg):
        self.messages.append(msg)
    
    def readUnreadMessages(self):
        unread =  self.messages[self.read:]
        read = len(self.messages)
        return unread

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  
ip = 'localhost'  
port = 4137 
server.connect((ip, port))  

chatHistory={}
def userInterface():
    completer = WordCompleter(['register', 'refresh_rooms', 'show_rooms', 'add', 'join', 'leave', 'disconnect', 'read', 'send'],
                             ignore_case=True)
    while 1:
        userInput = prompt('IRC>',
                        history=FileHistory('history.txt'),
                        auto_suggest=AutoSuggestFromHistory(),
                        completer=completer
                       )

        args = userInput.split(" ", 2)
        toSend = []
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


_thread.start_new_thread(userInterface,()) 

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