import socket
import sys
import os
import time
import threading
import hashlib
from bs4 import BeautifulSoup
from click.types import Path


def prefetchThread(s1, path, add, Line1, *serverdata):
    global cache
    print("*" * 100)
    print("Prefetch Decode")
    content = ''.join(map(str, serverdata))
    # print(content[0])
    # print(content)
    if path.endswith("/") != True:
        path = path + "/"
    if content.find("Content-Type: text/html") != -1:
        soup = BeautifulSoup(content, "html.parser")
        for a in soup.find_all('a', href=True):
            dummy = a['href']
            print(dummy)
            # Not needed ---- and dummy.find("/") == -1
            if dummy.find("http") == -1 and dummy.find("?") == -1:
                if dummy.startswith("/"):
                    dummy = dummy[1:]
                pathpre = path + dummy
                getpre = Line1.split(
                    ' ')[0] + " " + pathpre + " " + Line1.split(' ')[2] + "\n" + add
                print(getpre)
                getpreEn = getpre.encode()
                print("-" * 100)
                print("Doing prefetch for: ", dummy)
                s1.send(getpreEn)
                data2pre = s1.recv(51200)

                if len(data2pre) > 0:
                    cacheStorepre = hashlib.md5(pathpre.encode())
                    print(
                        "Inside prefetching and cache storing - after receiving from server")
                    startpre = time.time()
                    cache[cacheStorepre.hexdigest()] = startpre
                    recvpre = open(dummy, "wb")
                    recv1 = recvpre.write(data2pre)
                    recvpre.close()
                    print("file made via prefetch")
                else:
                    print("No data from server")
                    print("<<<<SEND ERROR MESSAGE TO CLIENT>>>>>")


def proxyThread(conn, client_addr, timerx):
    try:
        global cache
        print("In thread")
        print("client: " + str(conn) + "address: " + str(client_addr))
        print("Receiving data")
        data1 = conn.recv(51200)
        request = data1.decode()
        print("Data Decoded: ", request)
        Line1 = request.split('\n', 1)[0]
        url = Line1.split(' ')[1]
        http = 0
        print(Line1.split(' ')[2])
        if Line1.split(' ')[0] != "GET":
            print("HTTP method NOT served")
            http = 1  # or return 0 can be used
            status = Line1.split(
                ' ')[2] + " 400 Bad Request\n" + "Content-type: text/html\n\n"
            message = "<HTML><HEAD><TITLE>400 Bad Request Reason: Invalid Method</TITLE></HEAD><body>400 Bad Request Reason: Invalid Method<br>Oops Something Went Wrong<br></BODY></HTML>"
            conn.send((status + message).encode())

        if Line1.split(' ')[2].startswith("HTTP/1.0") or Line1.split(' ')[2].startswith("HTTP/1.1"):
            do = "nothing"
        else:
            status = Line1.split(
                ' ')[2] + " 501 Not Implemented\n" + "Content-type: text/html\n\n"
            message = "<HTML><HEAD><TITLE>501 Not Implemented: Invalid HTTP version</TITLE></HEAD><body>501 Not Implemented: Invalid HTTP version<br>Oops Something Went Wrong<br></BODY></HTML>"
            conn.send(status.encode())
            conn.send(message.encode())
            http = 1

        # if Line1.split(' ')[0]!="GET" or
        #url = url[1:]
        if http == 0:

            print("URL: ", url)
            http_locate = url.find("://")
            print("HTTP Position ", http_locate)
            if (http_locate == -1):
                TrueURL = url
            else:
                TrueURL = url[(http_locate + 3):]  # rest of url
            port_locate = TrueURL.find(":")
            path_locate = TrueURL.find("/")
            if path_locate == -1:
                path_locate = len(TrueURL)
                path = "/"
            else:
                path = TrueURL[path_locate:]
            #pathEn = path.encode()
            cacheSuccess = 0
            check = hashlib.md5(path.encode())
            for i in cache.keys():  # check cache and send if exists
                if check.hexdigest() == i:
                    current = cache[i]
                    current = int(current)
                    if time.time() - current < timerx:
                        print("Sending from CACHE for path: ", path)
                        fileCache = path.find(".")
                        if fileCache != -1:
                            lastLocC = path.rfind("/")
                            filenameCache = path[lastLocC + 1:]
                            # file path may have ? in middle followed by version
                            # number
                            newLoc1 = filenameCache.find("?")
                            if newLoc1 != -1:
                                filenameCache = filenameCache[:newLoc1]
                        else:
                            print("Sent Index file from cache")
                            filenameCache = path[:-1]
                            extractCache = filenameCache.rfind("/")
                            filenameCache = filenameCache[extractCache + 1:]

                        sendcache = open(filenameCache, "rb")
                        sendcache1 = sendcache.read()
                        conn.send(sendcache1)
                        conn.close()
                        cacheSuccess = 1
                        break

            if cacheSuccess == 0:
                add = request.split('\n', 1)[1]
                get = Line1.split(' ')[0] + " " + path + " " + \
                    Line1.split(' ')[2] + "\n" + add
                print("Get: ", get)
                getEn = get.encode()
                # default port
                if port_locate == -1 or path_locate < port_locate:
                    serverPort = 80
                    serverPath = TrueURL[:path_locate]
                    print("used if")
                else:
                    serverPort = int(TrueURL[port_locate + 1:path_locate])
                    serverPath = TrueURL[:port_locate]
                    print("used else")
                print("Let's connect to Server: {} and Port: {}".format(
                    serverPath, serverPort))
                try:
                    ResolveServer = socket.gethostbyname(serverPath)
                except:
                    print("ERROR. Could not resolve. Is your internet ON?")
                try:
                    s1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s1.connect((ResolveServer, serverPort))
                    # act as client and request data from actual server
                    s1.send(getEn)
                    # while 1:
                    # receive data from web server
                    data2 = s1.recv(51200)
                    try:
                        serverdata = data2.decode("ISO-8859-1")
                        print(serverdata)
                    except:
                        print(
                            "ERROR in printing serverdata. Did you change default encoding on CMD?")
                        return(0)
                    print("Length ", len(serverdata))

                    # pass
                    if len(serverdata) > 0:
                        if len(path) > 1:
                            file = path.find(".")  # get only last name after /
                            if file != -1:
                                lastLoc = path.rfind("/")
                                filename = path[lastLoc + 1:]
                                # strip the version number of file
                                newLoc = filename.find("?")
                                if newLoc != -1:
                                    filename = filename[:newLoc]
                            else:
                                filename = path[:-1]
                                extract = filename.rfind("/")
                                filename = filename[extract + 1:]

                            cacheStore = hashlib.md5(path.encode())
                            print(
                                "Inside cache storing - after receiving from server")
                            start = time.time()
                            cache[cacheStore.hexdigest()] = start
                            # x = cache.append(cacheStore.hexdigest()) #used during
                            # list (partial cache)
                            recv = open(filename, "wb")
                            recv1 = recv.write(data2)
                            recv.close()
                            print("file made")

                        conn.send(data2)
                    else:
                        print("No data from server")
                        print("<<<<SEND ERROR MESSAGE TO CLIENT>>>>>")
                        #err = "something"
                        #errEn = err.encode()
                        # conn.send(errEn)
                        # break

                    t1 = threading.Thread(
                        target=prefetchThread, args=(s1, path, add, Line1, serverdata))
                    print("Prefetch thread", t1.getName())
                    t1.daemon = True
                    t1.start()
                    t1.join()

                    s1.close()
                    conn.close()
                except socket.error as e1:
                    s1.close()
                    conn.close()
                    print("Runtime Error: ", str(e1))
                    sys.exit()
    except:
        status = Line1.split(
            ' ')[2] + " 500 Internal Server Error: cannot allocate memory\n" + "Content-type: text/html\n\n"
        message = "<HTML><HEAD><TITLE>500 Internal Server Error: cannot allocate memory</TITLE></HEAD><body>500 Internal Server Error: cannot allocate memory<br>Oops Something Went Wrong<br>Cannot allocate memory</BODY></HTML>"
        conn.send(status.encode())
        conn.send(message.encode())


def main():
    global cache
    if len(sys.argv) == 1:
        print("Error. Need at least one argument")
        print("Format: webProxy <port>& <optional-timeout>")
        print("System will exit")
        sys.exit()

    portx = sys.argv[1]

    timerx = sys.argv[2]
    print("1")
    try:
        timerx = float(timerx)
    except:
        print(
            "Error. Invalid timer argument. Timer argument should be positive real number")
        sys.exit()

    portL = len(portx)
    try:
        # to extract numbers only incase last value is '&'
        port = int(portx[0:portL])
    except:
        print(
            "Invalid format of port number. Usage webproxy <portnumber> <cache-timeout>&")
        print("System will exit")
        sys.exit()
    print("Port number:", port)
    if port >= 65535 or port <= 1024:
        print(
            "Error. Port number out of range. Please input between 1024-65535")
        print("System will exit")
        sys.exit()
    host = ""
    #port = 9997
    #timerx = 10
    try:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.bind((host, port))
            s.listen(400)
            cache = {}
            cache['redundant'] = "string"  # ensure dictioonary is never empty
        except socket.error as e:
            print(str(e))
            sys.exit()
        while 1:
            print("In while - accepting connections")
            conn, client_addr = s.accept()
            t = threading.Thread(
                target=proxyThread, args=(conn, client_addr, timerx))
            print(t.getName())
            t.daemon = True
            t.start()
            t.join()
        s.close()
    except KeyboardInterrupt:
        print("Keyboard Interrupt. Exiting")
        sys.exit()
if __name__ == '__main__':
    main()

quit()


