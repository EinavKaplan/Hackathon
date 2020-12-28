import socket
import struct
import msvcrt


team_name = "shirnav"
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
        client_socket.connect((server_ip, server_port))
        client_socket.send(team_name.encode('UTF-8'))
        return client_socket
    except socket.error:
        client_socket.close()
        return None


def game_mode(client_socket):
    welcome_msg = client_socket.recv(1024)
    print(welcome_msg)
    client_socket.setblocking(0)  # the socket now is non blocking
    game_over = False
    while not game_over:
        while not msvcrt.kbhit():
            try:
                msg = client_socket.recv(2048)
                if not msg:
                    game_over = True
                    break
                print(msg)
            except socket.error:
                continue
        if not game_over:
            send_key(msvcrt.getch(), client_socket)
    print("Server disconnected, listening for offer requests...")


def send_key(key, client_socket):
    client_socket.send(key)


if __name__ == "__main__":
    client_main()
