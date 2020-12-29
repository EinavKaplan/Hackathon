import socket
import struct
from threading import Thread
import time


DEST_PORT = 13117
TEAMS_THREADS = []
# TODO:: set port
SOURCE_PORT = 0


def server_main():
    # TODO:: set the IP address
    print("Server started, listening on IP address ")
    while True:
        server_tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_tcp_socket.bind(('', SOURCE_PORT))
        server_tcp_socket.listen(1)
        broadcast_offer_thread = Thread(sending_offers())
        connect_client_thread = Thread(connecting_clients(), server_tcp_socket)
        broadcast_offer_thread.start()
        connect_client_thread.start()
        broadcast_offer_thread.join()
        connect_client_thread.join()
        group1, group2 = divide_groups()
        game_mode(group1, group2)


def sending_offers():
    server_udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_udp_socket.bind(('', SOURCE_PORT))
    offer = struct.pack('LBH', 0xfeedbeef, 0x2, SOURCE_PORT)
    for i in range(10):
        server_udp_socket.sendto(offer, ('', DEST_PORT))
        time.sleep(1)


def connecting_clients(server_tcp_socket):
    while 1:
        connection_socket, client_address = server_tcp_socket.accept()
        team_name = connection_socket.recv(1024)
        team_thread = Thread(collect_chars(), connection_socket)
        TEAMS_THREADS.append((team_thread, team_name))


def divide_groups():
    half = len(TEAMS_THREADS)//2
    return TEAMS_THREADS[:half], TEAMS_THREADS[half:]


def collect_chars(connection_socket):
    welcome_message = """Welcome to Keyboard Spamming Battle Royale.\n 
                         Group 1:\n
                         ==\n
                         {teams_name}"""
    connection_socket.send(welcome_message)



def game_mode(group1, group2):
    #10 seconds
    for team in TEAMS_THREADS:
        team[0].start()
        team[0].join()

