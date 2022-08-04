import sys
from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
import db

clients = {}
addresses = {}

HOST = "127.0.0.1"
PORT = 5000
BUFSIZ = 1024
ADDR = (HOST, PORT)
SOCK = socket(AF_INET, SOCK_STREAM)
SOCK.bind(ADDR)


def accept_incoming_connections():
    while True:
        client, client_address = SOCK.accept()
        print("%s:%s has connected." % client_address)
        client.send("Greetings from the ChatRoom! ".encode("utf8"))
        client.send("Now type your name and press enter!".encode("utf8"))
        addresses[client] = client_address
        Thread(target=handle_client, args=(client, client_address)).start()


def handle_client(conn, addr):
    name = conn.recv(BUFSIZ).decode("utf8")
    while db.check_exists(name):
        conn.send(bytes("enter another name: ", "utf-8"))
        name = conn.recv(BUFSIZ).decode("utf8")
    welcome = 'Welcome %s! If you ever want to quit, type #quit to exit.' % name
    conn.send(bytes(welcome, "utf8"))
    ip = addresses[conn][0]
    port = addresses[conn][1]
    add_to_database(name, ip, port)
    msg = "%s from [%s] has joined the chat!" % (name, "{}:{}".format(addr[0], addr[1]))
    broadcast(bytes(msg, "utf8"))
    clients[conn] = name
    while True:
        msg = conn.recv(BUFSIZ)
        msg = str(msg, 'utf-8')
        msg = msg.rstrip("\n")
        if msg == "#quit":
            conn.send(str.encode(msg))
            conn.close()
            delete_from_database(clients[conn])
            del clients[conn]
            broadcast(bytes("%s has left the chat." % name, "utf7"))
            break
        elif msg == "#list":
            l = db.get_online_users()
            for i in l:
                message_to_client(str.encode(i), conn, name + ": ")
        elif msg == "#change":
            conn.send(bytes("enter new name: ", "utf-8"))
            newName = conn.recv(BUFSIZ).decode("utf8")
            while db.check_exists(newName.strip('\n')):
                conn.send(bytes("enter another name: ", "utf-8"))
                newName = conn.recv(BUFSIZ).decode("utf8")
            conn.send(bytes("name changed.", "utf-8"))
            db.change_name(name.strip('\n'), newName.strip('\n'))
            name = newName
            clients[conn] = newName
        elif msg == "#client":
            conn.send(bytes("enter name of user that you want communicate: ", "utf-8"))
            clientName = conn.recv(BUFSIZ).decode("utf8")
            while db.check_exists(clientName.strip('\n')) is False:
                conn.send(bytes("enter another name: ", "utf-8"))
                clientName = conn.recv(BUFSIZ).decode("utf8")
            conn.send(bytes("enter #quit to exit from messaging to "+clientName+" : "+"\n", "utf-8"))
            conn.send(bytes("enter your message to "+clientName+" : ", "utf-8"))
            while True:
                msg = conn.recv(BUFSIZ)
                # msg = str(msg, 'utf-8')
                # msg = msg.rstrip("\n")
                if str.encode("#quit") in msg:
                    break
                else:
                    message_to_client(msg, get_client(clientName), name + ": ")
        # else:
        #     broadcast(str.encode(msg), name + ": ")


def broadcast(msg, prefix=""):
    for sock in clients:
        sock.send(bytes(prefix, "utf8") + msg)


def message_to_client(msg, spec, prefix=""):
    for sock in clients:
        if sock == spec:
            sock.send(msg)


def add_to_database(name, ip, port):
    db.insert_user(name.strip('\n'), ip, port)


def get_client(name):
    for sock in clients:
        if clients[sock] == name:
            return sock


def delete_from_database(name):
    db.delete_user(name.strip('\n'))


def receive_message():
    msg = sys.stdin.readline()
    if msg.rstrip("\n") == "#list":
        l = db.get_online_users()
        for i in l:
            print(i)

if __name__ == "__main__":
    SOCK.listen(5)
    print("Chat Server has Started !!")
    print("Waiting for connections...")
    ACCEPT_THREAD = Thread(target=accept_incoming_connections)
    ACCEPT_THREAD.start()
    while True:
        receive_message()
    ACCEPT_THREAD.join()
    SOCK.close()
