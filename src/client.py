import socket
import struct
from select import select
import sys
import getch
import time
from threading import Thread


team_name = "shirnav\n"
UDP_PORT = 13117


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
    client_socket.bind(("", UDP_PORT))
    while True:
        offer, server_address = client_socket.recvfrom(4096)
        (cookie, msg_type, server_port) = struct.unpack('LBH', offer)
        if offer_is_valid(cookie, msg_type):
            client_socket.close()
            return server_port, server_address[0]


# check the msg - magic cookie , msg type port
def offer_is_valid(cookie, msg_type):
    if cookie == 0xfeedbeef and msg_type == 0x2:
        return True
    return False


def connect_to_server(server_port, server_ip):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        print("Received offer from "+server_ip+"."+server_port+", attempting to connect...\n")
        client_socket.connect((server_ip, server_port))
        client_socket.sendall(team_name.encode('UTF-8'))  # sendall?
        return client_socket
    except socket.error:
        close_tcp(client_socket)
        return None


def game_mode(client_socket):
    welcome_msg = client_socket.recv(1024)
    print(welcome_msg)
    # stop_thread = False
    # sending_keys = Thread(target=send_key, args=((lambda: stop_thread), client_socket))
    # sending_keys.start()
    # time.sleep(10)
    # stop_thread = True
    # msg = client_socket.recv(2048)
    # print(msg)
    client_socket.setblocking(0)
    game_over = False
    while not game_over:
        try:
            msg = client_socket.recv(2048)
            if not msg:
                game_over = True
                break
            print(msg)
        except socket.error:
            pass
        if not game_over and kbhit():
            client_socket.sendall(getch.getch().encode())
    close_tcp(client_socket)
    print("Server disconnected, listening for offer requests...\n")


# def send_key(stop, client_socket):
#     while not stop():
#         client_socket.sendall(getch.getch().encode())


def kbhit():
    dr, dw, de = select([sys.stdin], [], [], 0)
    return dr == 0


def close_tcp(client_socket):
    client_socket.shutdown(socket.SHUT_RDWR)
    client_socket.close()


if __name__ == "__main__":
    client_main()
