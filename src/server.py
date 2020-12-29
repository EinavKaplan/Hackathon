import socket
import struct
from threading import Thread, Lock
import time


DEST_PORT = 13117
TEAMS_THREADS_GROUP1 = []
TEAMS_THREADS_GROUP2 = []
COUNTER_GROUP1 = 0
COUNTER_GROUP2 = 0
SOURCE_IP = socket.gethostbyname(socket.gethostname())
SOURCE_PORT = 1610


def server_main():
    print("Server started, listening on IP address {ip}".format(ip=SOURCE_IP))
    while True:
        server_tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_tcp_socket.bind((SOURCE_IP, SOURCE_PORT))
        broadcast_offer_thread = Thread(target=sending_offers, args=())
        connect_client_thread = Thread(target=connecting_clients, args=(server_tcp_socket,))
        broadcast_offer_thread.start()
        connect_client_thread.start()
        broadcast_offer_thread.join()
        connect_client_thread.join()

        game_mode()


def sending_offers():
    server_udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_udp_socket.bind(('', SOURCE_PORT))
    offer = struct.pack('LBH', 0xfeedbeef, 0x2, SOURCE_PORT)
    for i in range(10):
        server_udp_socket.sendto(offer, ('', DEST_PORT))
        time.sleep(1)


def connecting_clients(server_tcp_socket):
    groups_divider = 0
    server_tcp_socket.listen(1)
    while 1:
        connection_socket, client_address = server_tcp_socket.accept()
        team_name = connection_socket.recv(1024)
        if groups_divider == 0:
            team_thread = Thread(target=collect_chars, args=(connection_socket, 1))
            TEAMS_THREADS_GROUP1.append((team_thread, 1, team_name, connection_socket))
            groups_divider = 1
        else:
            team_thread = Thread(target=collect_chars, args=(connection_socket, 2))
            TEAMS_THREADS_GROUP2.append((team_thread, 2, team_name, connection_socket))
            groups_divider = 0


def get_group_names(group_list):
    names = ""
    for t in group_list:
        x, y, name = t
        names = names+name
    return names


def collect_chars(connection_socket, group_num):
    welcome_message = """Welcome to Keyboard Spamming Battle Royale.\n 
                         Group 1:\n
                         ==\n
                         {group1_names}
                         Group 2:\n
                         ==\n
                         {group2_names}\n
                         Start pressing keys on your keyboard as fast as you can!!\n"""\
        .format(group1_names=get_group_names(TEAMS_THREADS_GROUP1), group2_names=get_group_names(TEAMS_THREADS_GROUP2))
    connection_socket.send(welcome_message)
    while 1:
        key = connection_socket.recv(1024)
        if group_num == 1:
            global COUNTER_GROUP1
            Lock().acquire()
            COUNTER_GROUP1 += 1
            Lock().release()
        else:
            global COUNTER_GROUP2
            Lock().acquire()
            COUNTER_GROUP2 += 1
            Lock.release()


def game_mode():
    all_teams = TEAMS_THREADS_GROUP1 + TEAMS_THREADS_GROUP2
    for team in all_teams:
        team[0].start()
        team[0].join()
    time.sleep(10)
    winners = 0
    group_names = ""
    if COUNTER_GROUP1 > COUNTER_GROUP2:
        winners = 1
        group_names = get_group_names(TEAMS_THREADS_GROUP1)
    else:
        winners = 2
        group_names = get_group_names(TEAMS_THREADS_GROUP2)
    game_over_message = """Game over!\n
                           Group 1 typed in {counter1} characters. Group 2 typed in {counter2} characters.\n
                           Group {winners} wins!\n
                           Congratulations to the winners:\n
                           ==\n
                           {winning_group}""".format(counter1=COUNTER_GROUP1, counter2=COUNTER_GROUP2,
                                                     winners=winners, winning_group=group_names)
    for team in all_teams:
        team[3].send(game_over_message)
        team[3].close()

