import socket
import struct
from threading import Thread, Lock
import time
from scapy.arch import get_if_addr

# constants
buff_len = 1024
MAGIC_COOKIE = 0xfeedbeef
MESSAGE_TYPE = 0x2
DEST_PORT = 13117
# global variables
TEAMS_THREADS_GROUP1 = []  # (team_thread, team_num, team_name, connection_socket)
TEAMS_THREADS_GROUP2 = []
COUNTER_GROUP1 = 0
COUNTER_GROUP2 = 0
SOURCE_IP = get_if_addr('eth1')  # ip development network  # socket.gethostbyname(socket.gethostname())
SOURCE_PORT = 2066
lock = Lock()


def server_main():
    print("Server started, listening on IP address {ip}".format(ip=SOURCE_IP))
    server_tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_tcp_socket.bind((SOURCE_IP, SOURCE_PORT))
    while True:
        broadcast_offer_thread = Thread(target=sending_offers, args=())
        connect_client_thread = Thread(target=connecting_clients, args=(server_tcp_socket,))
        connect_client_thread.start()
        broadcast_offer_thread.start()
        broadcast_offer_thread.join()
        connect_client_thread.join()
        game_mode()
        print("Game over, sending out offer request...")
        reset()


def sending_offers():
    server_udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_udp_socket.bind(('', SOURCE_PORT))
    offer = struct.pack('LBH', MAGIC_COOKIE, MESSAGE_TYPE, SOURCE_PORT)
    for i in range(10):
        server_udp_socket.sendto(offer, ('', DEST_PORT))
        time.sleep(1)


def connecting_clients(server_tcp_socket):
    groups_divider = 0
    server_tcp_socket.listen()
    server_tcp_socket.settimeout(1.0)
    start_time = time.time()
    elapsed = 0
    while elapsed < 10:
        elapsed = time.time() - start_time
        try:
            connection_socket, client_address = server_tcp_socket.accept()
            connection_socket.settimeout(1.0)
            got_team_name = False
            while not got_team_name:
                try:
                    team_name = connection_socket.recv(buff_len).decode("UTF-8")
                    got_team_name = True
                    if groups_divider == 0:
                        team_thread = Thread(target=collect_chars, args=(connection_socket, 1))
                        TEAMS_THREADS_GROUP1.append((team_thread, 1, team_name, connection_socket))
                        groups_divider = 1
                    else:
                        team_thread = Thread(target=collect_chars, args=(connection_socket, 2))
                        TEAMS_THREADS_GROUP2.append((team_thread, 2, team_name, connection_socket))
                        groups_divider = 0
                except:
                    elapsed = time.time() - start_time
                    if elapsed >= 10:
                        break
                    else:
                        pass
        except:
            pass


def get_group_names(group_list):
    names = ""
    for group in group_list:
        x, y, name, z = group
        names = names + name
    return names


def collect_chars(connection_socket, group_num):
    welcome_message = """Welcome to Keyboard Spamming Battle Royale.\nGroup 1:\n==\n{group1_names}\nGroup 2:\n==
    {group2_names}\nStart pressing keys on your keyboard as fast as you can!!"""\
        .format(group1_names=get_group_names(TEAMS_THREADS_GROUP1),
                group2_names=get_group_names(TEAMS_THREADS_GROUP2))
    connection_socket.send(welcome_message.encode("UTF-8"))
    start_time = time.time()
    elapsed = 0
    while elapsed < 10:
        elapsed = time.time() - start_time
        try:
            key = connection_socket.recv(buff_len).decode("UTF-8")
            if group_num == 1:
                global COUNTER_GROUP1
                lock.acquire()
                COUNTER_GROUP1 += 1
                lock.release()
            else:
                global COUNTER_GROUP2
                lock.acquire()
                COUNTER_GROUP2 += 1
                lock.release()
        except:
            pass


def game_mode():
    all_teams = TEAMS_THREADS_GROUP1 + TEAMS_THREADS_GROUP2
    for team in all_teams:
        team[0].start()
    for team in all_teams:
        team[0].join()
    if COUNTER_GROUP1 > COUNTER_GROUP2:
        game_over_message = """\tGame over!
    Group 1 typed in {counter1} characters. Group 2 typed in {counter2} characters.
    Group {winners} wins!\nCongratulations to the winners:\n==\n{winning_group}"""\
        .format(counter1=COUNTER_GROUP1,
                counter2=COUNTER_GROUP2,
                winners=1,
                winning_group=get_group_names(TEAMS_THREADS_GROUP1))
    elif COUNTER_GROUP1 < COUNTER_GROUP2:
        game_over_message = """\tGame over!
    Group 1 typed in {counter1} characters. Group 2 typed in {counter2} characters.
    Group {winners} wins!\nCongratulations to the winners:\n==\n{winning_group}"""\
        .format(counter1=COUNTER_GROUP1,
                counter2=COUNTER_GROUP2,
                winners=2,
                winning_group=get_group_names(TEAMS_THREADS_GROUP2))
    else:
        game_over_message = """\tGame over!
        Group 1 typed in {counter1} characters. Group 2 typed in {counter2} characters. 
        It's a tie!"""
    for team in all_teams:
        team[3].send(game_over_message.encode("UTF-8"))
        team[3].close()


def reset():
    global TEAMS_THREADS_GROUP1
    TEAMS_THREADS_GROUP1 = []
    global TEAMS_THREADS_GROUP2
    TEAMS_THREADS_GROUP2 = []
    global COUNTER_GROUP1
    COUNTER_GROUP1 = 0
    global COUNTER_GROUP2
    COUNTER_GROUP2 = 0


if __name__ == "__main__":
    server_main()
