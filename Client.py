import socket  
import sys  
import _thread
import time

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  
ip = 'localhost'  
port = 4137 
server.connect((ip, port))  
print(server)

def userInterface():
    while True:
        message = sys.stdin.readline()[:-1]  
        server.send(message.encode('utf-8')) 

_thread.start_new_thread(userInterface,()) 

while True:   
    data = server.recv(2048)
    if data:   
        print (data.decode('utf-8')) 

server.close()  