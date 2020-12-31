import socket
import struct
from select import select
import sys
import getch
from scapy.arch import get_if_addr


# constants
buff_len = 1024
MAGIC_COOKIE = 0xfeedbeef
MESSAGE_TYPE = 0x2
team_name = "shirnav\n"
UDP_PORT = 13117
SERVER_IP = ""


def client_main():
    print("Client started, listening for offer requests...")
    while True:
        server_port, server_ip = wait_for_offer()
        client_socket = connect_to_server(server_port, server_ip)
        if client_socket is None:
            continue
        game_mode(client_socket)


def wait_for_offer():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    client_socket.bind(("", UDP_PORT))
    while True:
        offer, server_address = client_socket.recvfrom(buff_len)
        global SERVER_IP
        SERVER_IP = server_address[0]
        try:
            (cookie, msg_type, server_port) = struct.unpack('LBH', offer)
            if offer_is_valid(cookie, msg_type):
                client_socket.close()
                return server_port, SERVER_IP
        except:
            pass


# check the msg - magic cookie , msg type port
def offer_is_valid(cookie, msg_type):
    if cookie == MAGIC_COOKIE and msg_type == MESSAGE_TYPE:
        return True
    return False


def connect_to_server(server_port, server_ip):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        print("Received offer from {ip} attempting to connect...\n".format(ip=server_ip))
        client_socket.connect((server_ip, server_port))
        client_socket.sendall(team_name.encode('UTF-8'))
        return client_socket
    except socket.error:
        return None


def game_mode(client_socket):
    welcome_msg = client_socket.recv(buff_len).decode("UTF-8")
    print(welcome_msg)
    client_socket.setblocking(0)
    game_over = False
    while not game_over:
        try:
            msg = client_socket.recv(buff_len).decode("UTF-8")
            if not msg:
                game_over = True
                break
            else:
                print(msg)
                game_over = True
                break
        except socket.error:
            pass
        if not game_over and not kbhit():
            try:
                client_socket.sendall(getch.getch().encode("UTF-8"))
            except socket.error:
                pass
    client_socket.close()
    print("Server disconnected, listening for offer requests...\n")


def kbhit():
    dr, dw, de = select([sys.stdin], [], [], 0)
    return dr == 0


def close_tcp(client_socket):
    client_socket.shutdown(socket.SHUT_RDWR)
    client_socket.close()


if __name__ == "__main__":
    client_main()
