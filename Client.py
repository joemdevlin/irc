import socket  
import select  
import sys  
  
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
ip = 'localhost'  
port = 4781 
server.connect((ip, port))  
  
while True:  
  
    # maintains a list of possible input streams  
    sockets_list = [sys.stdin, server]  
    read_sockets,write_socket, error_socket = select.select(sockets_list,[],[])  
  
    for socks in read_sockets:  
        if socks == server:  
            message = socks.recv(2048)  
            print (message.decode('utf-8'))  
        else:  
            message = sys.stdin.readline()  
            server.send(message)  
            sys.stdout.write("<You>")  
            sys.stdout.write(message)  
            sys.stdout.flush()  
server.close()  