# Python program to implement server side of chat room.  
import socket  
import sys  
import _thread
  
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  
    
ip = 'localhost'  
port = 4137
server.bind((ip, port))  
server.listen(10)  
  
clients = []  
  
# Spawning a serperate thread per conenction to relay the message
def clientthread(conn, addr):
    while True:  
            try:  
                data = conn.recv(2048)  
                if data: 
                    msg = "<" + addr[0] + "> " + data.decode('utf-8')
                    broadcast(msg.encode('utf-8'), conn)
                else: 
                    disconnect(conn)  
  
            except socket.error as e:
                print("ERROR: ") 
                print(e) 
                continue
  
def broadcast(message, connection):  
    for client in clients:  
        try:  
            client.send(message) 
            print("Message Sent") 
        except Exception as e:
            print("ERROR: ") 
            print(e)  
            client.close()   
            disconnect(client)  

def disconnect(client):  
    if client in clients:  
        clients.remove(client)  

if __name__ == '__main__':  
    try:
        while True:  
            conn, addr = server.accept()  
            print(conn)
            clients.append(conn)  
            print (addr[0] + " connected") 
        
            # creates and individual thread for every user  
            # that connects  
            _thread.start_new_thread(clientthread,(conn,addr)) 
            clientthread(conn, addr)
                    
    except KeyboardInterrupt:
        pass
    server.close()  