#!/usr/bin/env python3
"""
minecraft-vanilla_server_hibernation.py is used to start and stop automatically a vanilla minecraft server
Copyright (C) 2020  gekigek99
v4.2 (Python)
visit my github page: https://github.com/gekigek99
If you like what I do please consider having a cup of coffee with me at: https://www.buymeacoffee.com/gekigek99

Modified by dangercrow https://github.com/dangercrow
"""
import os
import socket
from threading import Timer, Lock, Thread, Event
from time import sleep
from typing import Callable

from data_usage import DataUsageMonitor
from inhibitors import PlayerBasedWinInhibitor
from server_state import ServerState

# ------------------------modify-------------------------------#

START_MINECRAFT_SERVER = 'cd PATH/TO/SERVERFOLDER; screen -dmS minecraftSERVER nice -19 java -jar minecraft_server.jar'  # set command to start minecraft-server service
STOP_MINECRAFT_SERVER = "screen -S minecraftSERVER -X stuff 'stop\\n'"  # set command to stop minecraft-server service

MINECRAFT_SERVER_STARTUPTIME = 20  # time the server needs until it is fully started
TIME_BEFORE_STOPPING_EMPTY_SERVER = 60  # time the server waits for clients to connect then it issues the stop command to server

# -----------------------advanced------------------------------#

LISTEN_HOST = "0.0.0.0"
LISTEN_PORT = 25555  # the port you will connect to on minecraft client

TARGET_HOST = "127.0.0.1"
TARGET_PORT = 25565  # the port specified on server.properties

DEBUG = False  # if true more additional information is printed

# ---------------------do not modify---------------------------#

data_monitor = DataUsageMonitor()
server_status = ServerState.OFFLINE
lock = Lock()

players = 0
timelefttillup = MINECRAFT_SERVER_STARTUPTIME
stopinstances = 0


def stop_empty_minecraft_server():
    global server_status, timelefttillup, stopinstances
    with lock:
        stopinstances -= 1
        if stopinstances > 0 or players > 0 or server_status == ServerState.OFFLINE:
            return
    server_status = ServerState.OFFLINE
    os.system(STOP_MINECRAFT_SERVER)
    print('MINECRAFT SERVER IS SHUTTING DOWN!')
    timelefttillup = MINECRAFT_SERVER_STARTUPTIME


def start_minecraft_server():
    global server_status, players
    if server_status != ServerState.OFFLINE:
        return
    server_status = ServerState.STARTING
    os.system(START_MINECRAFT_SERVER)
    print('MINECRAFT SERVER IS STARTING!')
    players = 0

    def _set_server_status_online():
        global server_status, stopinstances
        server_status = ServerState.ONLINE
        print('MINECRAFT SERVER IS UP!')
        with lock:
            stopinstances += 1
        Timer(TIME_BEFORE_STOPPING_EMPTY_SERVER, stop_empty_minecraft_server, ()).start()

    def _update_timeleft():
        global timelefttillup
        if timelefttillup > 0:
            timelefttillup -= 1

    set_interval(_update_timeleft, 1)

    Timer(MINECRAFT_SERVER_STARTUPTIME, _set_server_status_online, ()).start()


def set_interval(f: Callable, interval: float, *, thread_name=None):
    stop_event = Event()

    def thread_fn():
        while not stop_event.wait(interval):
            f()

    Thread(target=thread_fn, name=thread_name).start()
    return stop_event


def log_data_usage(data_usage_monitor: DataUsageMonitor, log_interval: float = 3) -> Event:
    return set_interval(lambda: print('{:.3f}KB/s'.format(data_usage_monitor.kilobytes_per_second)), log_interval)


def main():
    global players
    print('minecraft-vanilla-server-hibernation v4.2 (Python)')
    print('Copyright (C) 2020 gekigek99')
    print('visit my github page for updates: https://github.com/gekigek99')
    set_interval(lambda: PlayerBasedWinInhibitor.with_players(players), 1, thread_name="WinInhibitor")
    dock_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    dock_socket.setblocking(True)
    dock_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # to prevent errno 98 address already in use
    dock_socket.bind((LISTEN_HOST, LISTEN_PORT))
    dock_socket.listen(5)
    print('*** listening for new clients to connect...')
    if DEBUG:
        log_data_usage(data_monitor)
        printdatausage()
    while True:
        try:
            client_socket, client_address = dock_socket.accept()  # blocking
            if DEBUG:
                print('*** from {}:{} to {}:{}'.format(client_address[0], LISTEN_PORT, TARGET_HOST, TARGET_PORT))
            if server_status == ServerState.OFFLINE or server_status == ServerState.STARTING:
                connection_data_recv = client_socket.recv(64)
                if connection_data_recv[
                    -1] == 2:  # \x02 is the last byte of the first message when player is trying to join the server
                    player_data_recv = client_socket.recv(
                        64)  # here it's reading an other packet containing the player name
                    player_name = player_data_recv[3:].decode('utf-8', errors='replace')
                    if server_status == ServerState.OFFLINE:
                        print(player_name, 'tryed to join from', client_address[0])
                        start_minecraft_server()
                    if server_status == ServerState.STARTING:
                        print(player_name, 'tryed to join from', client_address[0], 'during server startup')
                        sleep(0.01)  # necessary otherwise it could throw an error:
                        # Internal Exception: io.netty.handler.codec.Decoder.Exception java.lang.NullPointerException
                        # the padding to 88 chars is important, otherwise someclients will fail to interpret
                        # (byte 0x0a (equal to \n or new line) is used to put the phrase in the center of the screen)
                        client_socket.sendall(("e\0c{\"text\":\"" + (f"Server is starting. Please wait. Time left: {timelefttillup} seconds").ljust(88, '\x0a') + "\"}").encode())
                else:
                    if connection_data_recv[-1] == 1:  # \x01 is the last byte of the first message when requesting server info
                        if server_status == ServerState.OFFLINE:
                            print('player unknown requested server info from', client_address[0])
                        if server_status == ServerState.STARTING:
                            print('player unknown requested server info from', client_address[0],
                                  'during server startup')
                client_socket.shutdown(1)  # sends FIN to client
                client_socket.close()
                continue
            if server_status == ServerState.ONLINE:
                server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                server_socket.connect((TARGET_HOST, TARGET_PORT))
                connectsocketsasync(client_socket, server_socket)
        except Exception as e:
            print(f"Exception in main(): {e}")


def connectsocketsasync(client, server):
    Thread(target=clienttoserver, name="ClientToServer", args=(client, server)).start()
    Thread(target=servertoclient, name="ServerToClient", args=(server, client)).start()


def clienttoserver(source, destination):
    global players, stopinstances
    players += 1
    print(f"A PLAYER JOINED THE SERVER! - {players} players online")
    forwardsync(source, destination)
    players -= 1
    print(f"A PLAYER LEFT THE SERVER! - {players} players remaining")
    with lock:
        stopinstances += 1
    Timer(TIME_BEFORE_STOPPING_EMPTY_SERVER, stop_empty_minecraft_server, ()).start()


def servertoclient(source, destination):
    forwardsync(source, destination)


# this thread passes data between connections
def forwardsync(source, destination):
    source.settimeout(60)
    destination.settimeout(60)
    try:
        while True:
            data = source.recv(1024)
            if not data:  # if there is no data stop listening, this means the socket is closed
                break
            destination.sendall(data)
            with lock:
                data_monitor.used_bytes(len(data))
    except IOError as e:
        if e.errno == 32:  # user/server disconnected normally. has to be catched, because there is a race condition
            return  # when trying to check if destination.recv does return data
        print(f"IOError in forward(): {e}")
    except Exception as e:
        print(f"Exception in forward(): {e}")


if __name__ == '__main__':
    main()
