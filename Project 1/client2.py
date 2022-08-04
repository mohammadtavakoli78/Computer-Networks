import sys
from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
import os
from time import sleep


def receive():
    while True:
        try:
            msg = sock.recv(BUFSIZ).decode("utf8")
            if "#file" in msg:
                print("salam")
                add = sock.recv(BUFSIZ).decode("utf8")
                print(add.split(".", 1)[1])
                i = 1
                direction = os.path.dirname(__file__)
                path = "test."+add.split(".", 1)[1].rstrip("\n")
                print(path)
                file_path = os.path.join(direction, path)
                f = open(file_path, 'wb')
                i = i + 1
                while True:
                    print("1")
                    content = sock.recv(BUFSIZ)
                    print("5\n"+str(content))
                    while content:
                        print(content)
                        f.write(content)
                        print(2)
                        content = sock.recv(BUFSIZ)
                        print(content)
                        if "#finish" in bytes(str(content), "utf").decode("utf8"):
                            print(3)
                            f.close()
                            break
                    break
            else:
                print(msg)
        except OSError:
            break


def send(event=None):
    msg = sys.stdin.readline()
    if msg.rstrip("\n") == "#file":
        sock.send(bytes(msg, "utf8"))
        print('enter address of file :\n')
        address = sys.stdin.readline().rstrip("\n")
        sock.send(bytes(address, "utf8"))
        f = open(address, "rb")
        content = f.read(1024)
        while content:
            print(str(content)+"\n")
            sock.send(content)
            print(len(content))
            content = f.read(1024)
        sleep(5)
        sock.send(bytes("#finish", "utf8"))
    elif msg == "#quit":
        sock.close()
    else:
        sock.send(bytes(msg, "utf8"))



HOST = "127.0.0.1"
PORT = 5000
BUFSIZ = 1024
ADDR = (HOST, PORT)
sock = socket(AF_INET, SOCK_STREAM)
sock.connect(ADDR)

receive_thread = Thread(target=receive)
receive_thread.start()
while True:
    send()
