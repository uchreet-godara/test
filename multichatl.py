import eventlet
import logging

logging.basicConfig(filename='/home/uchreet/Desktop/logfile.log',
                    filemode='a',
                    format='[%(asctime)s] [%(name)s] [%(module)s:%(lineno)s] [%(levelname)s] %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.DEBUG)

logging.info("Running Urban Planning")

logger = logging.getLogger('urbanGUI')

from eventlet.green import socket
PORT = 3001
participants = {}


def extract_target_name_message(line):
    x = line.split(" ")
    target_name = (x[0][1:])
    message = " ".join(x[1:])
    return target_name, message


def send_message(writer, message):
    try:
        writer.write(message)
        writer.flush()
    except socket.error as e:
        if e[0] != 32:
            raise


def read_chats(writer, reader):
    writer.write("please enter your name: \n")
    writer.flush()
    name = reader.readline().strip()
    while name in participants:
        send_message(writer, "please enter your name again.it already exists : \n")
        name = reader.readline().strip()
    participants[name] = writer

    for n, wr in participants.items():
        if n is not name:
            send_message(wr, name + " has entered the room\n")

    line = reader.readline()
    while line:
        logger.info("chat: " + line.strip())
        target_name, message = extract_target_name_message(line)
        if target_name in participants:
            send_message(participants[target_name], name + ": " + message)
        else:
            for wr in participants:
                if participants[wr] is not writer:
                    send_message(participants[wr], name + ": " + line)
        line = reader.readline()
    del participants[name]
    logger.info("participant left chat")
    for n, wr in participants.items():
        send_message(wr, name + "has left the chat")



try:
    logger.info("Chatserver starting on port" + str(PORT))
    server = eventlet.listen(('0.0.0.0', PORT))
    while True:
        new_connection, address = server.accept()
        new_writer = new_connection.makefile('w')
        eventlet.spawn_n(read_chats, new_writer, new_connection.makefile('r'))
except(KeyboardInterrupt, SystemExit):
    logger.info('Chatserver exiting')
