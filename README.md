# irc

# Description
This project is an assignment for networking course.  The goal is to create an IRC like protocol and implement a server and client.

# Server
## Launching the server
The server has two optional command line arguments to set the ip address and port for the server to listen to TCP connections
![Commnad line image](https://github.com/joemdevlin/irc/guide/server_usage.png)

# Client
## Registering new user
To register a user name. use the register command
![client register image](https://github.com/joemdevlin/irc/guide/client_registration.png)

## Listing chat rooms
To display the available rooms, the client will have to first fetch the current room list from the server.  Then the usercan display the available rooms.
![client rooms image](https://github.com/joemdevlin/irc/guide/display_chat_rooms.png)

## Creating new chat rooms
The command below will create a new chat room.
![client rooms image](https://github.com/joemdevlin/irc/guide/create_chat_room.png)

## Chatting
To receive and send messages to a chat room, the user must first subscribe to the room.  Once a user has joined, they can send messages to that specific channel or multiple channels at once.
![client rooms image](https://github.com/joemdevlin/irc/guide/create_chat_room.png)
