# Python program to implement server side of chat room.  
import socket  
import sys  
import _thread
  
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  
    
ip = 'localhost'  
port = 4781
server.bind((ip, port))  
server.listen(10)  
  
clients = []  
  
# Spawning a serperate thread per conenction to relay the message
def clientthread(conn, addr):  
    conn.send("You there?".encode('utf-8'))  
  
    while True:  
            try:  
                data = conn.recv(2048)  
                if data: 
                    msg = "<" + addr[0] + "> " + data
                    print (msg)  
                    broadcast(msg, conn)  
  
                else:  
                    disconnect(conn)  
  
            except: 
                print("Error?") 
                continue
  
def broadcast(message, connection):  
    for client in clients:  
        if client!=connection:  
            try:  
                client.send(message)  
            except:  
                client.close()   
                disconnect(client)  

def disconnect(connection):  
    if client in clients:  
        client.remove(client)  

if __name__ == '__main__':  
    try:
        while True:  
            conn, addr = server.accept()  
            clients.append(conn)  
            print (addr[0] + " connected") 
        
            # creates and individual thread for every user  
            # that connects  
            _thread.start_new_thread(clientthread,(conn,addr)) 
                    
            conn.close()  
            server.close()  
    except KeyboardInterrupt:
        pass