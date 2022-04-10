from socket import *
import sys
import os
import threading

# Default server port for TCP connection for server
serverPort = 80

    
# Split the link into server name and directory
def splitLink(link):
    return link.split("/", 1)

# Get the body of the response
def getBody(head, get):
    message = get[len(head):]
    lines = []
    for line in message.splitlines():
        lines.append(line)
    return lines

def getBodySizeChar(head):
    for line in head.splitlines():
        if "Content-Length" in line:
            return int(line.split(":")[1].strip())

# Create GET request message
def createGETrequestMessage(directory, serverName, rangeStart=-1, rangeEnd=-1):
    if rangeStart > -1 and rangeEnd > -1:
        return "GET /%s HTTP/1.1\r\nHost:%s\r\nRange: bytes=%d-%d\r\n\r\n" % (directory, serverName, rangeStart, rangeEnd)
    return "GET /%s HTTP/1.1\r\nHost:%s\r\n\r\n" % (directory, serverName)

# Create HEAD request message
def createHEADrequestMessage(directory, serverName, rangeStart=-1, rangeEnd=-1):
    if rangeStart > -1 and rangeEnd > -1:
        return "HEAD /%s HTTP/1.1\r\nHost:%s\r\nRange: bytes=%d-%d\r\n\r\n" % (directory, serverName, rangeStart, rangeEnd)
    return "HEAD /%s HTTP/1.1\r\nHost: %s\r\n\r\n" % (directory, serverName)

# Create socket, connect to server and send request message
def prepareSocket(server_name, request_mes):
    clientSocket = createSocket()
    clientSocket.connect((server_name, serverPort))
    clientSocket.send(request_mes.encode())
    return clientSocket

# Create and return a socket
def createSocket():
    return socket(AF_INET, SOCK_STREAM)

# Get the response message from the server for each link in index file
def download_files(links, number_of_threads):    
    count = 1
    # Traverse through all the links in the index file
    for link in links:
        link_data = splitLink(link)
        requestMessageHead = createHEADrequestMessage(link_data[1], link_data[0])
        requestMessageGet = createGETrequestMessage(link_data[1], link_data[0])

        clientSocket = prepareSocket(link_data[0], requestMessageHead)

        # Get the response HEAD message from the buffer 
        responseHead = ""
        while True:
            resp_part = clientSocket.recv(4096)
            if resp_part == b'':
                break
            responseHead += resp_part.decode()
        clientSocket.close()

        clientSocket = prepareSocket(link_data[0], requestMessageGet)

        # Get the response GET message from the buffer
        responseGet = ""
        while True:
            resp_part = clientSocket.recv(4096)
            if resp_part == b'':
                break
            responseGet += resp_part.decode()
        clientSocket.close()

        # Check the response status code and if the status code is 200, save the file if no range is specified
        if "200 OK" in responseHead.splitlines()[0]:
            length = getBodySizeChar(responseHead)
            if length == None:
                print("%d. %s is not found." %(count, link))
                continue

            dictionary = {}
            file_parts = []
            lengths = []

            if length % number_of_threads == 0:
                for i in range(number_of_threads):
                    interval = str(i * length // number_of_threads) + ":" + str((i + 1) * length // number_of_threads - 1)
                    file_parts.append(interval)
                    lengths.append(((i + 1) * length // number_of_threads - 1) - (i * length // number_of_threads) + 1)
                    thread = threading.Thread(target=downloader_thread, args=(link_data, i * length // number_of_threads, (i + 1) * length // number_of_threads - 1, dictionary, i))
                    thread.start()
                    thread.join()
            else:
                for i in range(number_of_threads):
                    start_byte = i * (length // number_of_threads + 1)
                    end_byte = ((length // number_of_threads) * (i + 1)) + i

                    if end_byte >= length:
                        end_byte = length - 1

                    if start_byte >= length:
                        interval = str(end_byte) + ":" + str(end_byte)
                        file_parts.append(interval)
                        lengths.append(0)
                    else:
                        thread = threading.Thread(target=downloader_thread, args=(link_data, start_byte, end_byte, dictionary, i))
                        interval = str(start_byte) + ":" + str(end_byte)
                        file_parts.append(interval)
                        lengths.append(end_byte - start_byte + 1)
                        thread.start()
                        thread.join()
                
            
            print("%d. %s (size = %d) is downloaded." %(count, link, length))
            file_parts_str = ""
            for i in file_parts:
                # if i is last index
                if i == file_parts[-1]:
                    file_parts_str += i + "(" + str(lengths[file_parts.index(i)]) + ")"
                else:
                    file_parts_str += i + "(" + str(lengths[file_parts.index(i)]) + ")" + ", "

            print("File parts: " + file_parts_str)
                
            file_parts = []

            s = convert_dictionary_to_string(dictionary)
            save_file_message(link_data[1], s)
        else:
            print("%d. %s is not found." %(count, link))
        count += 1

# Take inputs from dictionary and convert them to a single string
def convert_dictionary_to_string(dictionary):
    string = ""
    for key in dictionary:
        string += dictionary[key]
    return string


def getBody_message(head, get):
    message = get[len(head):]
    return message

# Create thread with function and parameters
def createThread(function, parameters):
    thread = threading.Thread(target=function, args=parameters)
    return thread

def downloader_thread(link_data, lower_endpoint, upper_endpoint, dictionary, thread_id):
    requestMessagePartialGET = createGETrequestMessage(link_data[1], link_data[0], lower_endpoint, upper_endpoint)
    requestMessagePartialHEAD = createHEADrequestMessage(link_data[1], link_data[0], lower_endpoint, upper_endpoint)

    clientSocket = prepareSocket(link_data[0], requestMessagePartialGET)
    responsePartialGET = ""
    while True:
        resp_part = clientSocket.recv(4096)
        if resp_part == b'':
            break
        responsePartialGET += resp_part.decode()
                    
    clientSocket.close()

    clientSocket = prepareSocket(link_data[0], requestMessagePartialHEAD)

    responsePartialHEAD = ""
    while True:
        resp_part = clientSocket.recv(4096)
        if resp_part == b'':
            break
        responsePartialHEAD += resp_part.decode()
 
    clientSocket.close()

    # Add getBody_message(responsePartialHEAD, responsePartialGET) to dictionary with thread_id as key
    dictionary[thread_id] = getBody_message(responsePartialHEAD, responsePartialGET)

def save_file_message(file_name, body):
    file_name = file_name.replace("/", "")
    with open(os.path.join(os.getcwd(), file_name), 'w') as f:
        f.write(body)
    f.close()

##############################################################
#                                                            #
#                                                            #
#                                                            #
##############################################################
index_file = ""
no_of_parallel_connections = 0

# Read the command line arguments
for i, arg in enumerate(sys.argv):
    # Index 0 is FileDownloader.py So we start at 1
    if i == 1:
        index_file = arg
    elif i == 2:
        no_of_parallel_connections = arg

index_file = splitLink(index_file)

# Specify server name and server port
serverName = index_file[0]
directory = index_file[1]

print("URL of the index file: %s" %sys.argv[1])
print("Number of parallel connections: %s" %sys.argv[2])

# Create client socket and GET message for the index file
requestMessageIndexGET = createGETrequestMessage(directory, serverName)
clientSocket = prepareSocket(serverName, requestMessageIndexGET)

responseIndexGET = ""
while True:
    resp_part = clientSocket.recv(4096)
    if resp_part == b'':
        break
    responseIndexGET += resp_part.decode()
clientSocket.close()

requestMessageIndexHEAD = createHEADrequestMessage(directory, serverName)
clientSocket = prepareSocket(serverName, requestMessageIndexHEAD)

responseIndexHEAD = ""
while True:
    resp_part = clientSocket.recv(4096)
    if resp_part == b'':
        break
    responseIndexHEAD += resp_part.decode()
clientSocket.close()

file_count = -1

body = ""
if "200 OK" in responseIndexHEAD.splitlines()[0]:
    body = getBody(responseIndexHEAD, responseIndexGET)
    file_count = len(body)
    print("There are %d file URLs in the index file." % file_count)
    print("Index file is downloaded.")
else:
    print("ERROR: The index file is not found!\r\n" + responseIndexHEAD.splitlines()[0])
    sys.exit(1)

download_files(body, int(no_of_parallel_connections))
