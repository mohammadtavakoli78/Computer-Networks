from scapy.all import *
import socket
import datetime
import matplotlib.pyplot as plt
from threading import Thread
import os
from geoip import geolite2
import time

from scapy.layers.dns import DNS
from scapy.layers.http import HTTPRequest, HTTP
from scapy.layers.inet import TCP, IP, UDP, ICMP

id = {}
ip = {}
tcp_number = 0
udp_number = 0
icmp_number = 0
fragments = 0
packet_len = []
sockets = {}
http = 0
dns = 0
finish = False


def capture(pkt, type, receive_time):
    global tcp_number
    global udp_number
    global icmp_number

    direction = ""
    pro_type = ""

    if type is 0:
        pro_type = "TCP"
        tcp_number += 1
    elif type is 1:
        pro_type = "UDP"
        udp_number += 1
    elif type is 2:
        pro_type = "ICMP"
        icmp_number += 1

    if socket.gethostbyname(socket.gethostname()) == pkt[IP].dst:
        direction = "IN"
    else:
        direction = "OUT"

    if pkt[IP].src in ip:
        ip.update({pkt[IP].src: ip[pkt[IP].src]+1})
    else:
        ip[pkt[IP].src] = 1

    if type != 2:
        if pkt.sport in sockets:
            sockets.update({pkt.sport: sockets[pkt.sport]+1})
        else:
            sockets[pkt.sport] = 1

        if pkt.dport in sockets:
            sockets.update({pkt.dport: sockets[pkt.dport]+1})
        else:
            sockets[pkt.dport] = 1

    packet_len.append(len(pkt[IP]))

    if pkt.id in id:
        id.update({pkt.id: id[pkt.id]+1})
    else:
        id[pkt.id] = 1

    if type is 0:
        print(str("[") + str(receive_time) + str("]") + "  " +
              "{}-{}:{}".format(pro_type, direction, len(pkt[IP])) + " Bytes" + "    " +
              "SRC-MAC : " + str(pkt.src) + "    " +
              "DST-MAC : " + str(pkt.dst) + "    " +
              "SRC-PORT : " + str(pkt.sport) + "    " +
              "DST-PORT : " + str(pkt.dport) + "    " +
              "SRC-IP : " + str(pkt[IP].src) + "    " +
              "DST-IP : " + str(pkt[IP].dst) + "    " +
              "TTL : " + str(pkt.ttl) + "    " +
              "CHECK-SUM : " + str(pkt.chksum) + "    " +
              "SEQUENCE-NUMBER : " + str(pkt.seq) + "   " +
              "ACK : " + str(pkt.ack) + "   " +
              "WINDOW : " + str(pkt.window) + "    ")
    elif type == 1:
        print(str("[") + str(receive_time) + str("]") + "  " +
              "{}-{}:{}".format(pro_type, direction, len(pkt[IP])) + " Bytes" + "    " +
              "SRC-MAC : " + str(pkt.src) + "    " +
              "DST-MAC : " + str(pkt.dst) + "    " +
              "SRC-PORT : " + str(pkt.sport) + "    " +
              "DST-PORT : " + str(pkt.dport) + "    " +
              "SRC-IP : " + str(pkt[IP].src) + "    " +
              "DST-IP : " + str(pkt[IP].dst) + "    " +
              "TTL : " + str(pkt.ttl) + "   " +
              "CHECK-SUM : " + str(pkt.chksum))
    elif type == 2:
        print(str("[") + str(receive_time) + str("]") + "  " +
              "{}-{}:{}".format(pro_type, direction, len(pkt[IP])) + " Bytes" + "    " +
              "SRC-MAC : " + str(pkt.src) + "    " +
              "DST-MAC : " + str(pkt.dst) + "    " +
              "SRC-IP : " + str(pkt[IP].src) + "    " +
              "DST-IP : " + str(pkt[IP].dst) + "    " +
              "TTL : " + str(pkt.ttl) + "   " +
              "CHECK-SUM : " + str(pkt.chksum))


def network_monitoring(pkt):
    global http
    global dns
    receive_time = datetime.datetime.now()
    if finish:
        print_ip()
        exit(0)
    if pkt.haslayer(IP):
        if pkt.haslayer(HTTP):
            http += 1
        if pkt.haslayer(DNS):
            dns += 1
        if pkt.haslayer(TCP):
            capture(pkt, 0, receive_time)
        elif pkt.haslayer(UDP):
            capture(pkt, 1, receive_time)
        elif pkt.haslayer(ICMP):
            capture(pkt, 2, receive_time)


def take_input():
    global finish
    while True:
        user_input = input()
        if user_input == 'x':
            finish = True
            break


def print_ip():
    global packet_len
    global fragments
    total_packets = tcp_number + udp_number + icmp_number
    sorted_tuples = sorted(ip.items(), key=lambda item: item[1], reverse=True)
    sorted_dict = {k: v for k, v in sorted_tuples}
    for i, j in sorted_dict.items():
        print(i+"   ----->    "+str(j))
    print("\n")

    sorted_tuples_port = sorted(sockets.items(), key=lambda item: item[1], reverse=True)
    sorted_dict_port = {k: v for k, v in sorted_tuples_port}
    for i, j in sorted_dict_port.items():
        print(str(i)+"   ----->    "+str(j))
    print("\n")

    sorted_tuples_id = sorted(id.items(), key=lambda item: item[1], reverse=True)
    sorted_dict_id = {k: v for k, v in sorted_tuples_id}
    for i, j in sorted_dict_id.items():
        if j > 1:
            fragments += 1

    print("TCP : "+str(tcp_number))
    print("UDP : "+str(udp_number))
    print("HTTP : "+str(http))
    print("DNS : "+str(dns))
    print("ICMP : "+str(icmp_number)+"\n")

    sorted_packet_len = sorted(packet_len)
    min = sorted_packet_len[0]
    average = 0
    sum = 0
    max = sorted_packet_len[len(sorted_packet_len)-1]
    for i in sorted_packet_len:
        sum += i
    average = round(sum/len(sorted_packet_len), 2)
    print("MIN : "+str(min))
    print("MIN : "+str(average))
    print("MIN : "+str(max))
    print("FRAGMENTS : "+str(fragments))

    f = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "report.txt"), "w")
    f.write("Total packets : \n")
    f.write("   Total : "+str(total_packets)+"\n")
    f.write("   TCP : "+str(tcp_number)+"\n")
    f.write("   UDP : "+str(udp_number)+"\n")
    f.write("   ICMP : "+str(icmp_number)+"\n")
    f.write("   HTTP : "+str(http)+"\n")
    f.write("   DNS : "+str(dns)+"\n\n")
    f.write("IP lists : \n")
    for i, j in sorted_dict.items():
        f.write("   "+i+"   ----->    "+str(j)+"\n")
    f.write("\n\nSocket lists : \n")
    for i, j in sorted_dict_port.items():
        f.write("   "+str(i)+"   ----->    "+str(j)+"\n")
    f.write("\n\n"+"Number of Fragment packet is : "+str(fragments)+"\n\n")
    f.write("Packet length : \n")
    f.write("   MIN length : "+str(min)+"   Bytes\n")
    f.write("   AVERAGE length : "+str(average)+"   Bytes\n")
    f.write("   MAX length : "+str(max)+"   Bytes\n")
    f.close()

    labels = 'TCP', 'UDP', 'ICMP'
    colors = ['yellowgreen', 'lightcoral', 'gold']
    sizes = [tcp_number, udp_number, icmp_number]

    plt.pie(sizes, labels=labels, autopct='%1.1f%%', shadow=True, startangle=140)

    plt.axis('equal')
    plt.show()


if __name__ == '__main__':
    receive_thread = Thread(target=take_input)
    receive_thread.start()
    sniff(prn=network_monitoring)
